package org.library.bookservice.service;

import event.BookDeletedEvent;
import lombok.RequiredArgsConstructor;
import org.library.bookservice.dao.AbstractDao;
import org.library.bookservice.dao.BookDao;
import org.library.bookservice.integration.producer.BookMetadataChangedProducer;
import org.library.bookservice.model.Book;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.kafka.core.KafkaTemplate;
import org.springframework.stereotype.Service;

@RequiredArgsConstructor
@Service
public class BookService extends AbstractService<Book> {

    private final BookDao dao;
    private final KafkaTemplate<String, BookDeletedEvent> kafkaTemplate;
    private final BookMetadataChangedProducer bookMetadataChangedProducer;

    @Value("${kafka.topics.book-deleted:book-deleted}")
    private String bookDeletedTopic;

    @Override
    protected AbstractDao<Book> getDao() {
        return dao;
    }

    @Override
    public Book save(Book entity) {
        Book saved = super.save(entity);
        bookMetadataChangedProducer.publishCreated(saved);
        return saved;
    }

    @Override
    protected void afterUpdate(Book entity) {
        bookMetadataChangedProducer.publishUpdated(entity);
    }

    @Override
    protected void afterDelete(Book entity) {
        kafkaTemplate.send(bookDeletedTopic, new BookDeletedEvent(entity.getId()));
    }
}
