package com.fsecure.atlant.examples.scanner;

public class InvalidInvocationException extends RuntimeException {
    public InvalidInvocationException(String message, Throwable cause) {
        super(message, cause);
    }

    public InvalidInvocationException(String message) {
        super(message);
    }
}
