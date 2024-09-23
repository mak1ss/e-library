package org.library.bookservice.dao;

import lombok.AllArgsConstructor;
import org.library.bookservice.model.Author;
import org.library.bookservice.repository.AuthorRepository;
import org.library.bookservice.repository.PrimaryRepository;
import org.springframework.stereotype.Service;

@AllArgsConstructor
@Service
public class AuthorDao extends AbstractDao<Author> {

    private AuthorRepository repo;

    @Override
    protected PrimaryRepository<Integer, Author> getRepository() {
        return repo;
    }
}
