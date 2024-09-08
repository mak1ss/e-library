package org.library.bookservice.dto.book;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;

import org.library.bookservice.dto.AbstractRequest;

import java.time.LocalDate;
import java.util.List;

@EqualsAndHashCode(callSuper = true)
@Builder
@Data
public class BookRequest extends AbstractRequest {

    @Size(min = 1, max = 255, message = "Specified title is too long. Max length is 255")
    @NotBlank
    private String title;

    @NotNull
    private Integer authorId;

    @NotNull
    private Integer categoryId;

    @NotNull
    private List<Integer> genreIdList;

    @Size(max = 500, message = "Specified description is too long. Max length is 500")
    private String description;

    @org.hibernate.validator.constraints.ISBN
    private String ISBN;

    @NotNull
    private Integer publisherId;

    private LocalDate releaseDate;

    @NotNull
    private Double price;
}
