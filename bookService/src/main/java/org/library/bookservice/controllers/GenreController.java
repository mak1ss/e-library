package org.library.bookservice.controllers;

import lombok.AllArgsConstructor;
import org.library.bookservice.dto.genre.GenreRequest;
import org.library.bookservice.dto.genre.GenreResponse;
import org.library.bookservice.mapper.GenreMapper;
import org.library.bookservice.mapper.Mapper;
import org.library.bookservice.model.Genre;
import org.library.bookservice.service.AbstractService;
import org.library.bookservice.service.GenreService;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@AllArgsConstructor
@RequestMapping("/api/genres")
public class GenreController extends AbstractController<Genre, GenreRequest, GenreResponse> {

    private final GenreService service;
    private final GenreMapper mapper;

    @Override
    protected AbstractService<Genre> getService() {
        return service;
    }

    @Override
    protected Mapper<Genre, GenreResponse, GenreRequest> getMapper() {
        return mapper;
    }
}
