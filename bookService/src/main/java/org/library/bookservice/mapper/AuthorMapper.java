package org.library.bookservice.mapper;

import org.library.bookservice.dto.author.AuthorRequest;
import org.library.bookservice.dto.author.AuthorResponse;
import org.library.bookservice.model.Author;
import org.springframework.stereotype.Service;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

@Service
public class AuthorMapper implements Mapper<Author, AuthorResponse, AuthorRequest> {


    @Override
    public Author requestToEntity(AuthorRequest request, Optional<Integer> id) {
        Author entity = new Author();
        entity.setId(id.orElse(null));

        entity.setName(request.getName());
        entity.setBio(request.getBio());

        return entity;
    }

    @Override
    public AuthorResponse entityToResponse(Author entity) {

        return AuthorResponse.builder()
                .id(entity.getId())
                .name(entity.getName())
                .bio(entity.getBio())
                .build();
    }

    @Override
    public List<AuthorResponse> entitiesToListResponse(Collection<Author> entityList) {
        return entityList.stream().map(this::entityToResponse).toList();
    }
}
