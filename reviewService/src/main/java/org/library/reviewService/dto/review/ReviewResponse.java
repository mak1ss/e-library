package org.library.reviewService.dto.review;

import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;
import org.library.reviewService.dto.AbstractResponse;

@Data
@EqualsAndHashCode(callSuper=false)
@Builder
public class ReviewResponse extends AbstractResponse {

    private Integer userId;

    private Integer bookId;

    private Integer rating;

    private String text;
}
