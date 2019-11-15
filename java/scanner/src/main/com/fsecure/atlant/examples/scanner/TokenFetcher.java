package com.fsecure.atlant.examples.scanner;

import java.util.stream.Collectors;
import java.net.URI;
import java.util.Map;
import java.util.HashMap;
import java.util.Set;
import java.io.IOException;
import java.io.InputStream;
import static java.util.Map.entry;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import static java.net.http.HttpRequest.BodyPublishers;
import java.net.http.HttpResponse;
import static java.net.http.HttpResponse.BodyHandlers;
import java.io.UnsupportedEncodingException;

import org.json.JSONTokener;
import org.json.JSONObject;
import org.json.JSONException;

class TokenFetcher
{ 
    private static final String AUDIENCE = "f-secure-atlant";

    private URI tokenEndpoint;
    private HttpClient client;

    public TokenFetcher(URI authorizationAddress) {
        this(HttpClient.newBuilder().build(), authorizationAddress);
    }

    public TokenFetcher(HttpClient client, URI authorizationAddress) {
        this.client = client;
        tokenEndpoint = URI.create(String.format("%s/api/token/v1",
                                                 authorizationAddress.toString()));
    }

    public Token fetch(String clientID, String clientSecret)
        throws IOException, InterruptedException {
        return fetch(clientID, clientSecret, Set.of());
    }


    public Token fetch(String clientID, String clientSecret, Set<String> scopes)
        throws IOException, InterruptedException {
        HttpRequest tokenRequest = buildTokenRequest(clientID, clientSecret, scopes);
        HttpResponse<InputStream> response =
            client.send(tokenRequest, BodyHandlers.ofInputStream());
        try {
            return deserializeTokenResponse(response.body());
        } catch (JSONException e) {
            throw new APIException("Invalid scan response", e);
        }
    }

    private Token deserializeTokenResponse(InputStream responseBody) {
        JSONTokener tokener = new JSONTokener(responseBody);
        JSONObject tokenResponse = new JSONObject(tokener);
        String token = tokenResponse.getString("access_token");
        int expiresIn = tokenResponse.getInt("expires_in");
        return new Token(token, expiresIn);
    }

    private HttpRequest buildTokenRequest(String clientID, String clientSecret, Set<String> scopes) {
        HashMap<String, String> params = new HashMap<String, String>();
        params.put("grant_type", "client_credentials");
        params.put("client_id", clientID);
        params.put("client_secret", clientSecret);
        params.put("audience", AUDIENCE);

        if (!scopes.isEmpty()) {
            params.put("scope", encodeScopes(scopes));
        }

        String queryParams =
            encodeQueryParameters(params);

        return HttpRequest.newBuilder()
            .uri(tokenEndpoint)
            .header("Content-Type", "application/x-www-form-urlencoded")
            .POST(BodyPublishers.ofString(queryParams))
            .build();
    }

    private String encodeQueryParameters(Map<String, String> params) {
        return params.entrySet()
            .stream()
            .map(entry -> {
                    try {
                        String key = URLEncoder.encode(entry.getKey(), StandardCharsets.UTF_8.toString());
                        String value = URLEncoder.encode(entry.getValue(), StandardCharsets.UTF_8.toString());
                        return String.format("%s=%s", key, value);
                    } catch (UnsupportedEncodingException e) {
                        throw new IllegalArgumentException(e);
                    }
                })
            .collect(Collectors.joining("&"));
    }

    private String encodeScopes(Set<String> scopes) {
        return scopes.stream()
            .collect(Collectors.joining(" "));
    }
} 
