package org.library.reviewService.client;

import org.library.reviewService.client.response.BookResponse;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;

@FeignClient(name = "book-service", url = "${book-service.url}")
public interface BookServiceClient {

    @RequestMapping(method = RequestMethod.GET, value = "/api/books/{bookId}")
    ResponseEntity<BookResponse> getById(@PathVariable Integer bookId);
}
