package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"net/url"
	"os"
	"strconv"
	"strings"
	"time"
)

type tokenInfo struct {
	Token     string `json:"access_token"`
	ExpiresIn int    `json:"expires_in"`
}

type authError struct {
	Type        string `json:"error"`
	Description string `json:"error_description"`
}

func (err *authError) Error() string {
	return fmt.Sprintf("%s: %s", err.Type, err.Description)
}

func fetchToken(address, clientID, clientSecret string, scopes []string) (
	token *tokenInfo,
	err error,
) {
	form := url.Values{}
	form.Set("grant_type", "client_credentials")
	form.Set("client_id", clientID)
	form.Set("client_secret", clientSecret)
	form.Set("audience", "f-secure-atlant")
	if len(scopes) > 0 {
		form.Set("scope", strings.Join(scopes, " "))
	}

	var response *http.Response
	response, err = http.PostForm(
		fmt.Sprintf("https://%s/api/token/v1", address),
		form,
	)
	if err != nil {
		return
	}
	defer response.Body.Close()

	if response.StatusCode == 200 {
		token = &tokenInfo{}
		err = json.NewDecoder(response.Body).Decode(token)
		return
	}

	authErr := authError{}
	err = json.NewDecoder(response.Body).Decode(&authErr)
	if err != nil {
		return
	}

	err = &authErr
	return
}

type scanDetection struct {
	Category   string  `json:"category"`
	Name       string  `json:"name"`
	MemberName *string `json:"member_name"`
}

type scanResponse struct {
	Status     string          `json:"status"`
	Result     *string         `json:"scan_result"`
	Detections []scanDetection `json:"detections"`
}

func (api *scanAPI) makeScanRequest(file *os.File) (
	request *http.Request,
	err error,
) {
	type metadata struct{}

	var meta []byte
	meta, err = json.Marshal(&metadata{})
	if err != nil {
		return
	}

	buffer := &bytes.Buffer{}
	multiWriter := multipart.NewWriter(buffer)

	var metaPart, dataPart io.Writer
	metaPart, err = multiWriter.CreateFormField("metadata")
	if err != nil {
		return
	}

	_, err = io.WriteString(metaPart, string(meta))
	if err != nil {
		return
	}

	dataPart, err = multiWriter.CreateFormField("data")
	if err != nil {
		return
	}

	_, err = io.Copy(dataPart, file)
	if err != nil {
		return
	}

	err = multiWriter.Close()
	if err != nil {
		return
	}

	request, err = http.NewRequest(
		"POST",
		fmt.Sprintf("https://%s/api/scan/v1", api.address),
		buffer,
	)

	if err != nil {
		return
	}
	request.Header.Set("Content-Type", multiWriter.FormDataContentType())
	request.Header.Set("Authorization", fmt.Sprintf("Bearer %s", api.token))

	return
}

type scanAPI struct {
	address string
	token   string
	client  http.Client
}

func newScanAPI(address, token string) *scanAPI {
	return &scanAPI{
		address: address,
		token:   token,
	}
}

func (api *scanAPI) scanFile(filePath string) (
	result *scanResponse,
	pollURL *string,
	retryAfter time.Duration,
	err error,
) {
	var file *os.File
	file, err = os.Open(filePath)
	if err != nil {
		return
	}
	defer file.Close()

	var request *http.Request
	request, err = api.makeScanRequest(file)
	if err != nil {
		return
	}

	var response *http.Response
	response, err = api.client.Do(request)
	if err != nil {
		return
	}
	defer response.Body.Close()

	if response.StatusCode == 202 {
		location := response.Header.Get("Location")
		pollURL = &location

		var retryAfterSeconds int64
		retryAfterHeader := response.Header.Get("Retry-After")
		retryAfterSeconds, err = strconv.ParseInt(retryAfterHeader, 10, 32)
		if err != nil {
			return
		}
		retryAfter = time.Duration(retryAfterSeconds) * time.Second
	}

	if response.StatusCode == 200 || response.StatusCode == 202 {
		result = &scanResponse{}
		err = json.NewDecoder(response.Body).Decode(result)
		return
	}

	err = fmt.Errorf(
		"unexpected response from scanning server (status: %d)",
		response.StatusCode,
	)

	return
}

func (api *scanAPI) pollTask(taskURL string) (
	result *scanResponse,
	retryAfter time.Duration,
	err error,
) {

	var request *http.Request
	request, err = http.NewRequest("GET", fmt.Sprintf("https://%s%s", api.address, taskURL), nil)
	if err != nil {
		return
	}

	request.Header.Set("Authorization", fmt.Sprintf("Bearer %s", api.token))

	var response *http.Response
	response, err = api.client.Do(request)
	if err != nil {
		return
	}
	defer response.Body.Close()

	if response.StatusCode == 200 {
		result = &scanResponse{}
		err = json.NewDecoder(response.Body).Decode(result)
		if err != nil {
			return
		}

		if result.Status == "pending" {
			var retryAfterSeconds int64
			retryAfterHeader := response.Header.Get("Retry-After")
			retryAfterSeconds, err = strconv.ParseInt(retryAfterHeader, 10, 32)
			if err != nil {
				return
			}
			retryAfter = time.Duration(retryAfterSeconds) * time.Second
		}

		return
	}

	err = fmt.Errorf(
		"unexpected response from scanning server (status: %d)",
		response.StatusCode,
	)

	return
}

func errorExit(err string) {
	fmt.Fprintf(os.Stderr, "error: %s\n", err)
	os.Exit(1)
}

func printResult(result *scanResponse) {
	fmt.Printf("result: %s\n", *result.Result)
	if len(result.Detections) > 0 {
		fmt.Println("detections:")
		for i, detection := range result.Detections {
			fmt.Printf("  %d. category: %s name: %s\n", i+1, detection.Category, detection.Name)
		}
	}
}

func waitResponse(wait time.Duration) {
	fmt.Printf("scan pending, checking again in %d seconds...\n", wait)
	time.Sleep(wait)
}

func main() {
	if len(os.Args) != 6 {
		errorExit("usage: atlant-scanner AUTH-URL SCAN-URL CLIENT-ID CLIENT-SECRET FILE")
	}

	authURL := os.Args[1]
	scanURL := os.Args[2]
	clientID := os.Args[3]
	clientSecret := os.Args[4]
	filePath := os.Args[5]

	token, err := fetchToken(
		authURL,
		clientID,
		clientSecret,
		[]string{"scan"},
	)

	if err != nil {
		errorExit(err.Error())
	}

	scanner := newScanAPI(scanURL, token.Token)

	scanResponse, taskURL, pollAfter, err := scanner.scanFile(filePath)
	if err != nil {
		errorExit(err.Error())
	}

	switch scanResponse.Status {
	case "complete":
		printResult(scanResponse)
	case "pending":
		waitResponse(pollAfter)
		for {
			scanResponse, pollAfter, err := scanner.pollTask(*taskURL)
			if err != nil {
				errorExit(err.Error())
			}
			switch scanResponse.Status {
			case "complete":
				printResult(scanResponse)
				return
			case "pending":
				waitResponse(pollAfter)
			default:
				errorExit("unknown scan status")
			}
		}
	default:
		errorExit("unknown scan status")
	}
}
