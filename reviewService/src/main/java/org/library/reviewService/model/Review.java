package org.library.reviewService.model;

import lombok.Data;
import org.library.reviewService.model.base.Archivable;
import org.library.reviewService.model.base.Identifiable;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

import java.time.LocalDateTime;

@Data
@Document(collection = "reviews")
public class Review implements Identifiable, Archivable {

    @Id
    private String id;

    private String userId;

    private String firstName;

    private String lastName;

    private String avatarUrl;

    private Integer bookId;

    private LocalDateTime createdAt;

    private Integer rating;

    @Field(write = Field.Write.ALWAYS)
    private String text;

    private boolean archived;

    /**
     * Semantic relevance score computed asynchronously by the recommender service.
     * NULL until ReviewScoringResultListener processes the result event.
     * Score range: [0.0, 1.0] where 1.0 = highly relevant, 0.0 = not relevant.
     */
    private ReviewScoringResult scoringResult;
}
