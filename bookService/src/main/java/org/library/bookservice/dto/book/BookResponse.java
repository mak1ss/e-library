package org.library.bookservice.dto.book;

import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;
import org.library.bookservice.dto.AbstractResponse;
import org.library.bookservice.dto.author.AuthorResponse;
import org.library.bookservice.dto.category.CategoryResponse;
import org.library.bookservice.dto.genre.GenreResponse;
import org.library.bookservice.dto.publisher.PublisherResponse;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

@EqualsAndHashCode(callSuper = true)
@Builder
@Data
public class BookResponse extends AbstractResponse {

    private Integer id;
    private String title;
    private AuthorResponse author;
    private CategoryResponse category;
    private String description;
    private String ISBN;
    private PublisherResponse publisher;
    private LocalDate releaseDate;
    private BigDecimal price;
    private List<GenreResponse> bookGenres;
}
