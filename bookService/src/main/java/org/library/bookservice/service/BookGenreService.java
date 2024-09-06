package org.library.bookservice.service;

import lombok.AllArgsConstructor;
import org.library.bookservice.dao.AbstractDao;
import org.library.bookservice.dao.BookGenreDao;
import org.library.bookservice.model.BookGenre;
import org.springframework.stereotype.Service;

@AllArgsConstructor
@Service
public class BookGenreService extends AbstractService<BookGenre> {

    private BookGenreDao dao;

    @Override
    protected AbstractDao<BookGenre> getDao() {
        return dao;
    }
}
