package org.library.bookservice.service;

import event.BookDeletedEvent;
import lombok.AllArgsConstructor;
import org.library.bookservice.dao.AbstractDao;
import org.library.bookservice.dao.BookDao;
import org.library.bookservice.model.Book;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

@AllArgsConstructor
@Service
public class BookService extends AbstractService<Book> {

    private BookDao dao;

    private final KafkaTemplate<String, BookDeletedEvent> kafkaTemplate;

    @Override
    protected AbstractDao<Book> getDao() {
        return dao;
    }

    @Override
    protected void afterDelete(Book entity) {
        kafkaTemplate.send("book-deleted", new BookDeletedEvent(entity.getId()));
    }
}
