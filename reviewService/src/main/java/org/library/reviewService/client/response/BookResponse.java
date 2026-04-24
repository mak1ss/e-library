package org.library.reviewService.client.response;

import lombok.Data;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

/**
 * Book response DTO matching the bookService /api/books/{bookId} response.
 * This DTO is used to deserialize the API response from bookService.
 */
@Data
public class BookResponse {
    private Integer id;
    private String title;
    
    /**
     * Author object - contains id, name, bio
     */
    private AuthorResponse author;
    
    /**
     * Category object - contains id, name, description
     */
    private CategoryResponse category;
    
    private String description;
    private String ISBN;
    
    /**
     * Publisher object - contains id, name, country
     */
    private PublisherResponse publisher;
    
    private LocalDate releaseDate;
    private BigDecimal price;
    private String imageUrl;
    
    /**
     * List of genre objects - each contains id, name, description
     */
    private List<GenreResponse> bookGenres;
    
    private Double averageRating;
    private Integer totalReviews;
    
    /**
     * Simple DTO for Author - extracted from author object
     */
    @Data
    public static class AuthorResponse {
        private Integer id;
        private String name;
        private String bio;
    }
    
    /**
     * Simple DTO for Category - extracted from category object
     */
    @Data
    public static class CategoryResponse {
        private Integer id;
        private String name;
        private String description;
    }
    
    /**
     * Simple DTO for Publisher - extracted from publisher object
     */
    @Data
    public static class PublisherResponse {
        private Integer id;
        private String name;
        private String country;
    }
    
    /**
     * Simple DTO for Genre - extracted from bookGenres list
     */
    @Data
    public static class GenreResponse {
        private Integer id;
        private String name;
        private String description;
    }
}
