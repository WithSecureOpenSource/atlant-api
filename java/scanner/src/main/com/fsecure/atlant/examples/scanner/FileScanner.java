package com.fsecure.atlant.examples.scanner;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import static java.net.http.HttpRequest.BodyPublishers;
import java.net.http.HttpResponse;
import static java.net.http.HttpResponse.BodyHandlers;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.FileNotFoundException;
import java.nio.charset.StandardCharsets;
import java.util.Optional;
import java.util.ArrayList;
import java.util.List;
import java.time.Duration;

import org.json.JSONTokener;
import org.json.JSONObject;
import org.json.JSONArray;
import org.json.JSONException;

class FileScanner
{ 

    private URI baseURI;
    private URI scanEndpoint;
    private URI pollEndpoint;
    private HttpClient client;
    private Authenticator authenticator;
    private Token token;

    public FileScanner(URI scanningAddress, Authenticator authenticator)
        throws IOException, InterruptedException {
        this(HttpClient.newBuilder().build(), scanningAddress, authenticator);
    }

    public FileScanner(HttpClient client, URI scanningAddress, Authenticator authenticator)
        throws IOException, InterruptedException {
        this.authenticator = authenticator;
        this.client = client;

        baseURI = scanningAddress;
        scanEndpoint = URI.create(String.format("%s/api/scan/v1",
                                                scanningAddress.toString()));
        pollEndpoint = URI.create(String.format("%s/api/poll/v1",
                                                scanningAddress.toString()));

        refreshToken();
    }

    public void refreshToken()
        throws IOException, InterruptedException {
        token = this.authenticator.fetchToken();
    }

    public ScanResult scan(ScanMetadata metadata, String path)
        throws FileNotFoundException, IOException, InterruptedException {
        return scan(metadata, new FileInputStream(path));
    }

    public ScanResult scan(ScanMetadata metadata, InputStream input)
        throws IOException, InterruptedException {
        HttpRequest scanRequest = buildScanRequest(metadata, input);
        HttpResponse<InputStream> response =
            client.send(scanRequest, BodyHandlers.ofInputStream());
        return processScanResponse(response);
    }

    private ScanResult processScanResponse(HttpResponse<InputStream> response) {
        ScanResult scanResult = null;
        
        int statusCode = response.statusCode();
        if (statusCode == 200 || statusCode == 202) {
            try {
                scanResult = deserializeScanResponse(response.body());
            } catch (JSONException e) {
                throw new APIException("Invalid scan response", e);
            }
        } else {
            throw new APIException("Unexpected response from scanning service");
        }

        if (statusCode == 202) {
            Optional<String> location = response.headers().firstValue("Location");
            if (!location.isPresent()) {
                throw new APIException("Missing poll URL");
            }

            scanResult.setPollURL(location);

            Optional<String> retryAfter = response.headers().firstValue("Retry-After");
            if (!retryAfter.isPresent()) {
                throw new APIException("Missing retry after duration");
            }

            try {
                Duration duration = Duration.ofSeconds(Long.parseLong(retryAfter.get()));
                scanResult.setRetryAfter(Optional.of(duration));
            } catch (NumberFormatException e) {
                throw new APIException("Invalid retry after duration", e);
            }
        }

        return scanResult;
    }

    public ScanResult poll(String pollURL)
        throws IOException, InterruptedException {
        HttpRequest pollRequest = buildPollRequest(pollURL);
        HttpResponse<InputStream> response =
            client.send(pollRequest, BodyHandlers.ofInputStream());
        return processPollResponse(response);
    }

    private HttpRequest buildScanRequest(ScanMetadata metadata,
                                         InputStream input)
        throws IOException {
        byte[] metadataBody =
            serializeScanMetadata(metadata).getBytes(StandardCharsets.UTF_8);
        MultiPartBuilder multiPartBuilder = new MultiPartBuilder()
            .addPart(new MultiPartBuilder.Part("metadata", "application/json", metadataBody))
            .addPart(new MultiPartBuilder.Part("data", "application/octet-stream", input));
        byte[] body = multiPartBuilder.encode();

        return HttpRequest.newBuilder()
            .uri(scanEndpoint)
            .header("Content-Type",
                    String.format("multipart/form-data; boundary=%s", multiPartBuilder.getBoundary()))
            .header("Authorization",
                    String.format("Bearer %s", token.getToken()))
            .POST(BodyPublishers.ofByteArray(body))
            .build();
    }

    private HttpRequest buildPollRequest(String pollURL) {
        URI fullPollURL = URI.create(String.format("%s%s", baseURI.toString(), pollURL));
        return HttpRequest.newBuilder()
            .uri(fullPollURL)
            .header("Authorization", String.format("Bearer %s", token.getToken()))
            .GET()
            .build();
    }

    private ScanResult processPollResponse(HttpResponse<InputStream> response) {
        ScanResult scanResult = null;
        
        int statusCode = response.statusCode();
        if (statusCode == 200) {
            try {
                scanResult = deserializeScanResponse(response.body());
            } catch (JSONException e) {
                throw new APIException("Invalid scan response", e);
            }
        } else {
            throw new APIException("Unexpected response from scanning service");
        }

        if (scanResult.getStatus() == ScanResult.Status.PENDING) {
            Optional<String> retryAfter = response.headers().firstValue("Retry-After");
            if (!retryAfter.isPresent()) {
                throw new APIException("Missing retry after duration");
            }

            try {
                Duration duration = Duration.ofSeconds(Long.parseLong(retryAfter.get()));
                scanResult.setRetryAfter(Optional.of(duration));
            } catch (NumberFormatException e) {
                throw new APIException("Invalid retry after duration", e);
            }
        }

        return scanResult;
    }

    private ScanResult deserializeScanResponse(InputStream responseBody) {
        JSONTokener tokener = new JSONTokener(responseBody);
        JSONObject scanResponse = new JSONObject(tokener);

        String scanStatus = scanResponse.getString("status");
        ScanResult.Status status;
        switch (scanStatus) {
        case "complete":
            status = ScanResult.Status.COMPLETE;
            break;
        case "pending":
            status = ScanResult.Status.PENDING;
            break;
        default:
            throw new APIException("Invalid scan status");
        }

        String scanResult = scanResponse.getString("scan_result");
        ScanResult.Result result;
        switch (scanResult) {
        case "clean":
            result = ScanResult.Result.CLEAN;
            break;
        case "whitelisted":
            result = ScanResult.Result.WHITELISTED;
            break;
        case "suspicious":
            result = ScanResult.Result.SUSPICIOUS;
            break;
        case "PUA":
            result = ScanResult.Result.PUA;
            break;
        case "UA":
            result = ScanResult.Result.UA;
            break;
        case "harmful":
            result = ScanResult.Result.HARMFUL;
            break;
        default:
            throw new APIException("Invalid detection category");
        }

        JSONArray scanDetections = scanResponse.getJSONArray("detections");
        List<Detection> detections = new ArrayList<Detection>();
        for (int i = 0; i < scanDetections.length(); i++) {
            Detection detection = buildDetection(scanDetections.getJSONObject(i));
            detections.add(detection);
        }

        return new ScanResult(status, result, detections);
    }

    private Detection buildDetection(JSONObject object) {
        String detectionCategory = object.getString("category");
        Detection.Category category;
        switch (detectionCategory) {
        case "suspicious":
            category = Detection.Category.SUSPICIOUS;
            break;
        case "PUA":
            category = Detection.Category.PUA;
            break;
        case "UA":
            category = Detection.Category.UA;
            break;
        case "harmful":
            category = Detection.Category.HARMFUL;
            break;
        default:
            throw new APIException("Invalid detection category");
        }

        String name = object.getString("name");

        Optional<String> member =
            Optional.ofNullable(object.optString("member_name", null));

        return new Detection(category, name, member);
    }

    private String serializeScanMetadata(ScanMetadata metadata) {
        return metadata.toJSONObject().toString();
    }
} 
