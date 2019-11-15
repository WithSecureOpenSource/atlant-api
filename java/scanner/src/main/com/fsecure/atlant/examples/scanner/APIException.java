package com.fsecure.atlant.examples.scanner;

public class APIException extends RuntimeException {
    public APIException(String message, Throwable cause) {
        super(message, cause);
    }

    public APIException(String message) {
        super(message);
    }
}

