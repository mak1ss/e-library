package org.library.bookservice.controllers;

import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.library.bookservice.dto.book.BookRequest;
import org.library.bookservice.dto.book.BookResponse;
import org.library.bookservice.filtering.model.EntityFilterSpecificationBuilder;
import org.library.bookservice.filtering.model.book.BookSpecificationBuilder;
import org.library.bookservice.mapper.BookMapper;
import org.library.bookservice.mapper.Mapper;
import org.library.bookservice.model.Book;
import org.library.bookservice.service.AbstractService;
import org.library.bookservice.service.BookService;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.NoSuchElementException;

@Slf4j
@RestController
@AllArgsConstructor
@RequestMapping("/api/books")
public class BookController extends AbstractController<Book, BookRequest, BookResponse> {

    private final BookService service;
    private final BookMapper mapper;

    private final BookSpecificationBuilder specificationBuilder;

    @Override
    protected AbstractService<Book> getService() {
        return service;
    }

    @Override
    protected Mapper<Book, BookResponse, BookRequest> getMapper() {
        return mapper;
    }

    @Override
    protected EntityFilterSpecificationBuilder<Book> getSpecificationBuilder() {
        return specificationBuilder;
    }

    @Override
    protected void executeEntityDelete(Integer id) {
        getService().getById(id).ifPresentOrElse(book -> {
            if(book.isArchived()) {
               log.info("Archived book was tried to delete. ID: {}", book.getId());
               return;
            }
            getService().delete(book);
        }, () -> {
            throw new NoSuchElementException();
        });
    }
}
