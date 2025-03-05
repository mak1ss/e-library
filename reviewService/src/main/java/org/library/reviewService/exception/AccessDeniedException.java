package org.library.reviewService.exception;

public class AccessDeniedException extends RuntimeException {

    public AccessDeniedException() {}

    public AccessDeniedException(String message) {
        super(message);
    }
}
