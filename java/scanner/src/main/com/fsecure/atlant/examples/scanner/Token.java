package com.fsecure.atlant.examples.scanner;

class Token
{ 
    private String token;
    private int expiration;

    public Token(String token, int expiration) {
        this.token = token;
        this.expiration = expiration;
    }

    public String getToken() {
        return token;
    }

    public int getExpiration() {
        return expiration;
    }
}

