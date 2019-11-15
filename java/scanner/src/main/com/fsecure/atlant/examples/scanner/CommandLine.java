package com.fsecure.atlant.examples.scanner;

import java.net.URI;

class CommandLine {
    public static final String USAGE =
        "Usage: AUTH-ADDR SCAN-ADDR CLIENT-ID CLIENT-SECRET FILE";

    private URI authorizationAddress;
    private URI scanAddress;
    private String clientID;
    private String clientSecret;
    private String inputFile;

    public CommandLine(String args[]) {
        if (args.length != 5) {
            throw new InvalidInvocationException("Invalid number of arguments");
        }

        try {
            authorizationAddress = URI.create(String.format("https://%s", args[0]));
        } catch (IllegalArgumentException e) {
            throw new InvalidInvocationException("Invalid authorization server address", e);
        }

        try {
            scanAddress = URI.create(String.format("https://%s", args[1]));
        } catch (IllegalArgumentException e) {
            throw new InvalidInvocationException("Invalid scanning server address", e);
        }

        clientID = args[2];
        clientSecret = args[3];

        inputFile = args[4];
    }

    public URI getAuthorizationAddress() {
        return authorizationAddress;
    }

    public URI getScanAddress() {
        return scanAddress;
    }

    public String getClientID() {
        return clientID;
    }

    public String getClientSecret() {
        return clientSecret;
    }

    public String getInputFile() {
        return inputFile;
    }
}
