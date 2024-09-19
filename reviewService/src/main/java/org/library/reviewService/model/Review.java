package org.library.reviewService.model;

import lombok.Data;
import org.library.reviewService.model.base.Identifiable;
import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;
import org.springframework.data.mongodb.core.mapping.Field;

import java.time.LocalDateTime;

@Data
@Document(collection = "reviews")
public class Review implements Identifiable {

    @Id
    private String id;

    private Integer userId;

    private Integer bookId;

    private LocalDateTime createdAt;

    private Integer rating;

    @Field(write = Field.Write.ALWAYS)
    private String text;
}
