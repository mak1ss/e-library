package org.library.bookservice.dto.genre;

import jakarta.validation.constraints.NotBlank;
import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;
import org.hibernate.validator.constraints.Length;
import org.library.bookservice.dto.AbstractRequest;

@EqualsAndHashCode(callSuper = true)
@Builder
@Data
public class GenreRequest extends AbstractRequest {

    @NotBlank
    @Length(min = 1, max = 50, message = "Specified name is too long. Max length is 50")
    private String name;

    @NotBlank
    @Length(max = 255, message = "Specified description is too long. Max length is 255")
    private String description;
}
