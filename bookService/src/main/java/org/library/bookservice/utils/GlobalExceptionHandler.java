package org.library.bookservice.utils;

import lombok.extern.slf4j.Slf4j;
import org.springdoc.api.ErrorMessage;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.NoHandlerFoundException;

import java.nio.file.AccessDeniedException;
import java.util.NoSuchElementException;

@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler({IllegalArgumentException.class})
    public ResponseEntity<ErrorMessage> handleIllegalArgumentException(
            IllegalArgumentException ex) {
        log.error("Illegal argument:" , ex);

        String message = "Illegal argument, please try again: " + ex.getMessage();

        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(new ErrorMessage(message));
    }

    @ExceptionHandler({MethodArgumentNotValidException.class, MissingServletRequestParameterException.class})
    public ResponseEntity<ErrorMessage> handleBadRequest(
            Exception ex) {

        log.error("Bad request:" , ex);

        String message = "Bad request, please try again: " + ex.getMessage();
        return ResponseEntity.status(HttpStatus.BAD_REQUEST).body(new ErrorMessage(message));
    }

    @ExceptionHandler({DataIntegrityViolationException.class})
    public ResponseEntity<ErrorMessage> handleConflict(
            DataIntegrityViolationException ex) {
        log.error("Conflict: " , ex);

        String message = "Conflict with existing data: " + ex.getMessage();

        return ResponseEntity.status(HttpStatus.CONFLICT).body(new ErrorMessage(message));
    }

    @ExceptionHandler({NoHandlerFoundException.class, NoSuchElementException.class})
    public ResponseEntity<Object> handleResourceNotFoundException(
            NoSuchElementException ex) {

        log.error("Resource not found:", ex);

        String message = "Resource not found: " + ex.getMessage();

        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(new ErrorMessage(message));
    }

    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<ErrorMessage> handleAccessDeniedException(
            AccessDeniedException exception) {

        log.error("Access denied:", exception);

        String message = "Access denied for your request: " + exception.getMessage();

        return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body(new ErrorMessage(message));
    }

    @ExceptionHandler(UnsupportedOperationException.class)
    public ResponseEntity<ErrorMessage> handleUnsupportedOperationException(
            UnsupportedOperationException ex){
        log.error("Unsupported operation:", ex);

        String message = "Unsupported operation: " + ex.getMessage();

        return ResponseEntity.status(HttpStatus.METHOD_NOT_ALLOWED).body(new ErrorMessage(message));
    }


    @ExceptionHandler({Exception.class})
    public ResponseEntity<ErrorMessage> handleAllExceptions(Exception ex) {
        log.error("Unhandled exception:", ex);

        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                .body(new ErrorMessage("Internal Server Error"));
    }
}
