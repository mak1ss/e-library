package org.library.bookservice.datagen;

import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

@Data
public class BookSeedDto {
    private String title;
    private String isbn;
    private String description;
    private LocalDate releaseDate;
    private BigDecimal price;
    private String imageKey;
    
    private String category;
    private String publisher;
    private String author;
    private List<String> genres;
}