package org.library.bookservice.dao;

import lombok.AllArgsConstructor;
import org.library.bookservice.model.Genre;
import org.library.bookservice.repository.GenreRepository;
import org.library.bookservice.repository.PrimaryRepository;
import org.springframework.stereotype.Service;

@AllArgsConstructor
@Service
public class GenreDao extends AbstractDao<Genre> {

    private GenreRepository repo;

    @Override
    protected PrimaryRepository<Integer, Genre> getRepository() {
        return repo;
    }
}
