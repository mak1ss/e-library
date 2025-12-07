package org.library.bookservice.service.listener;

import event.BookRatingUpdatedEvent;
import jakarta.transaction.Transactional;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.library.bookservice.service.BookService;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@Slf4j
@RequiredArgsConstructor
@Service
public class BookRatingUpdateListener {

    private final BookService bookService;

    @KafkaListener(topics = "book-rating-updated", groupId = "book-service-group")
    @Transactional
    public void handleBookRatingUpdate(BookRatingUpdatedEvent event) {
        log.info("Received rating update for book {}: {}", event.getBookId(), event.getAverageRating());

        bookService.getById(event.getBookId()).ifPresentOrElse(book -> {
            book.setAverageRating(event.getAverageRating());
            book.setTotalReviews(event.getTotalReviews());
        }, () -> log.warn("Book not found for rating update: {}", event.getBookId()));
    }
}
