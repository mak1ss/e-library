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
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardCopyOption;
import java.util.NoSuchElementException;
import java.util.Optional;
import java.util.UUID;

@RequiredArgsConstructor
@Service
public class BookService extends AbstractService<Book> {

    private final BookDao dao;
    private final KafkaTemplate<String, BookDeletedEvent> kafkaTemplate;
    private final BookMetadataChangedProducer bookMetadataChangedProducer;

    @Value("${kafka.topics.book-deleted:book-deleted}")
    private String bookDeletedTopic;

    @Value("${data.book.images.location}")
    private String imagesLocation;

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

    public Book uploadCoverImage(Integer bookId, MultipartFile file) {
        Book book = getById(bookId).orElseThrow(() -> new NoSuchElementException("Book not found: " + bookId));

        String extension = Optional.ofNullable(file.getOriginalFilename())
                .filter(name -> name.contains("."))
                .map(name -> name.substring(name.lastIndexOf(".")))
                .orElse(".jpg");

        String imageKey = "book-" + bookId + "-" + UUID.randomUUID() + extension;

        try {
            Path dir = Path.of(imagesLocation);
            Files.createDirectories(dir);

            if (book.getImageKey() != null) {
                Files.deleteIfExists(dir.resolve(book.getImageKey()));
            }

            Files.copy(file.getInputStream(), dir.resolve(imageKey), StandardCopyOption.REPLACE_EXISTING);
        } catch (IOException e) {
            throw new RuntimeException("Failed to store cover image", e);
        }

        book.setImageKey(imageKey);
        return update(book);
    }
}
