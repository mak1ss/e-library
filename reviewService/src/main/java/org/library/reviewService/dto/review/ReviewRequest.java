package org.library.reviewService.dto.review;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;
import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;
import org.library.reviewService.dto.AbstractRequest;

@Data
@EqualsAndHashCode(callSuper=false)
@Builder
public class ReviewRequest extends AbstractRequest {

    @NotNull
    private Integer userId;

    @NotNull
    private Integer bookId;

    @Min(1)
    @Max(5)
    private Integer rating;

    private String text;
}
