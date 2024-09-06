package org.library.bookservice.service;

import lombok.AllArgsConstructor;
import org.library.bookservice.dao.AbstractDao;
import org.library.bookservice.dao.AuthorDao;
import org.library.bookservice.model.Author;
import org.springframework.stereotype.Service;

@AllArgsConstructor
@Service
public class AuthorService extends AbstractService<Author> {

    private AuthorDao dao;

    @Override
    protected AbstractDao<Author> getDao() {
        return dao;
    }
}
