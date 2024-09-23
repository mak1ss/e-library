package org.library.reviewService.utils;

import feign.Response;
import feign.codec.ErrorDecoder;
import org.apache.coyote.BadRequestException;

import java.util.NoSuchElementException;

public class ClientErrorDecoder implements ErrorDecoder {

    @Override
    public Exception decode(String s, Response response) {
        return switch (response.status()) {
            case 400 -> new BadRequestException();
            case 404 -> new NoSuchElementException();
            default -> new Exception("Unhandled error: " + response.reason());
        };
    }
}
