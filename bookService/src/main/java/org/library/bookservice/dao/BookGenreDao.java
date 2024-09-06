package org.library.bookservice.dao;

import lombok.AllArgsConstructor;
import org.library.bookservice.model.BookGenre;
import org.library.bookservice.repository.BookGenreRepository;
import org.library.bookservice.repository.PrimaryRepository;
import org.springframework.stereotype.Service;

@AllArgsConstructor
@Service
public class BookGenreDao extends AbstractDao<BookGenre> {

    private BookGenreRepository repo;

    @Override
    protected PrimaryRepository<Integer, BookGenre> getRepository() {
        return repo;
    }
}
