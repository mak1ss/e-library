package org.library.bookservice.dto.review;

import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.time.LocalDateTime;

@Data
@EqualsAndHashCode(callSuper=false)
@Builder
public class ReviewResponse {

    private String id;

    private String userId;

    private String firstName;

    private String lastName;

    private String avatarUrl;

    private Integer bookId;

    private LocalDateTime createdAt;

    private Integer rating;

    private String text;
}