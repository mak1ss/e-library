package org.library.bookservice.mapper;

import org.library.bookservice.dto.genre.GenreRequest;
import org.library.bookservice.dto.genre.GenreResponse;
import org.library.bookservice.model.Genre;
import org.springframework.stereotype.Service;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

@Service
public class GenreMapper implements Mapper<Genre, GenreResponse, GenreRequest> {
    @Override
    public Genre requestToEntity(GenreRequest request, Optional<Integer> id) {
        Genre entity = new Genre();

        entity.setId(id.orElse(null));
        entity.setName(request.getName());
        entity.setDescription(request.getDescription());

        return entity;
    }

    @Override
    public GenreResponse entityToResponse(Genre entity) {

        return GenreResponse.builder()
                .id(entity.getId())
                .name(entity.getName())
                .description(entity.getDescription())
                .build();
    }

    @Override
    public List<GenreResponse> entitiesToListResponse(Collection<Genre> entityList) {
        return entityList.stream().map(this::entityToResponse).toList();
    }
}
