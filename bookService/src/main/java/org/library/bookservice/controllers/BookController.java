package org.library.bookservice.controllers;

import lombok.AllArgsConstructor;
import org.library.bookservice.dto.book.BookRequest;
import org.library.bookservice.dto.book.BookResponse;
import org.library.bookservice.mapper.BookMapper;
import org.library.bookservice.mapper.Mapper;
import org.library.bookservice.model.Book;
import org.library.bookservice.service.AbstractService;
import org.library.bookservice.service.BookService;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@AllArgsConstructor
@RequestMapping("/api/books")
public class BookController extends AbstractController<Book, BookRequest, BookResponse> {

    private final BookService service;
    private final BookMapper mapper;

    @Override
    protected AbstractService<Book> getService() {
        return service;
    }

    @Override
    protected Mapper<Book, BookResponse, BookRequest> getMapper() {
        return mapper;
    }
}
