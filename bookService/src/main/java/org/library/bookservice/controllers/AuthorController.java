package org.library.bookservice.controllers;

import lombok.AllArgsConstructor;
import org.library.bookservice.dto.author.AuthorRequest;
import org.library.bookservice.dto.author.AuthorResponse;
import org.library.bookservice.filtering.model.EntityFilterSpecificationBuilder;
import org.library.bookservice.filtering.model.author.AuthorSpecificationBuilder;
import org.library.bookservice.mapper.AuthorMapper;
import org.library.bookservice.mapper.Mapper;
import org.library.bookservice.model.Author;
import org.library.bookservice.service.AbstractService;
import org.library.bookservice.service.AuthorService;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@AllArgsConstructor
@RequestMapping("/api/authors")
public class AuthorController extends AbstractController<Author, AuthorRequest, AuthorResponse> {

    private AuthorService service;
    private AuthorMapper mapper;

    private final AuthorSpecificationBuilder specificationBuilder;

    @Override
    protected AbstractService<Author> getService() {
        return service;
    }

    @Override
    protected Mapper<Author, AuthorResponse, AuthorRequest> getMapper() {
        return mapper;
    }

    @Override
    protected EntityFilterSpecificationBuilder<Author> getSpecificationBuilder() {
        return specificationBuilder;
    }
}
