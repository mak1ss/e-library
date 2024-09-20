package org.library.bookservice.service;

import lombok.AllArgsConstructor;
import org.library.bookservice.dao.AbstractDao;
import org.library.bookservice.dao.GenreDao;
import org.library.bookservice.model.Genre;
import org.springframework.stereotype.Service;

@AllArgsConstructor
@Service
public class GenreService extends AbstractService<Genre> {

    private GenreDao dao;

    @Override
    protected AbstractDao<Genre> getDao() {
        return dao;
    }
}
