package org.library.bookservice.dto.category;

import jakarta.validation.constraints.NotBlank;
import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;
import org.hibernate.validator.constraints.Length;
import org.library.bookservice.dto.AbstractRequest;

@EqualsAndHashCode(callSuper = true)
@Builder
@Data
public class CategoryRequest extends AbstractRequest {

    @NotBlank
    @Length(max = 100, message = "Specified name is too long. Max length is 100")
    private String name;

    @NotBlank
    @Length(max = 255, message = "Specified description is too long. Max length is 255")
    private String description;
}
