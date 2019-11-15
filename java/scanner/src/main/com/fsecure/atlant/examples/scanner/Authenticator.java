package com.fsecure.atlant.examples.scanner;

import java.net.URI;
import java.io.IOException;
import java.util.Set;

class Authenticator
{ 
    private TokenFetcher tokenFetcher;
    private String clientID;
    private String clientSecret;
    private Set<String> scopes;

    public Authenticator(URI authorizationAddress,
                         String clientID,
                         String clientSecret,
                         Set<String> scopes) {
        this(new TokenFetcher(authorizationAddress), clientID, clientSecret, scopes);
    }

    public Authenticator(TokenFetcher tokenFetcher,
                         String clientID,
                         String clientSecret,
                         Set<String> scopes) {
        this.tokenFetcher = tokenFetcher;
        this.clientID = clientID;
        this.clientSecret = clientSecret;
        this.scopes = scopes;
    }

    public Token fetchToken()
        throws IOException, InterruptedException {
        return this.tokenFetcher.fetch(clientID, clientSecret, scopes);
    }
}
