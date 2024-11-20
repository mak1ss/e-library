package org.library.reviewService.eventListener;

import event.BookDeletedEvent;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.library.reviewService.service.ReviewService;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.stereotype.Service;

@Service
@AllArgsConstructor
@Slf4j
public class BookDeletedListener {

    private ReviewService reviewService;

    @KafkaListener(topics = "book-deleted")
    public void listener(BookDeletedEvent message) {
        log.info("Book deleted event fired: {}", message);
        reviewService.deleteByQuery(new Query(Criteria.where("bookId").is(message.getBookId())));
        log.info("Deleted reviews for book with id {}", message.getBookId());
    }
}
