package org.library.bookservice.service;

import lombok.AllArgsConstructor;
import org.library.bookservice.dao.AbstractDao;
import org.library.bookservice.dao.BookDao;
import org.library.bookservice.model.Book;
import org.springframework.stereotype.Service;

@AllArgsConstructor
@Service
public class BookService extends AbstractService<Book> {

    private BookDao dao;

    @Override
    protected AbstractDao<Book> getDao() {
        return dao;
    }
}
