package org.library.reviewService.client.response;

import lombok.Data;

import java.math.BigDecimal;

@Data
public class BookResponse {
    private Integer id;
    private String title;
    private String description;
    private String ISBN;
    private BigDecimal price;
}
