package org.library.bookservice.dao;

import lombok.AllArgsConstructor;
import org.library.bookservice.model.Book;
import org.library.bookservice.repository.BookRepository;
import org.library.bookservice.repository.PrimaryRepository;
import org.springframework.stereotype.Service;

@AllArgsConstructor
@Service
public class BookDao extends AbstractDao<Book> {

    private BookRepository repo;

    @Override
    protected PrimaryRepository<Integer, Book> getRepository() {
        return repo;
    }
}
