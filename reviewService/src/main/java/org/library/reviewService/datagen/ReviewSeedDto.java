package org.library.reviewService.datagen;

import lombok.Data;

@Data
public class ReviewSeedDto {
    private String userId;
    private String firstName;
    private String lastName;
    private String avatarUrl;
    private Integer bookId;
    private String createdAt;
    private Integer rating;
    private String text;
}