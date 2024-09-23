package org.library.bookservice.dto.author;


import jakarta.validation.constraints.NotBlank;
import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;
import org.hibernate.validator.constraints.Length;
import org.library.bookservice.dto.AbstractRequest;

@EqualsAndHashCode(callSuper = true)
@Builder
@Data
public class AuthorRequest extends AbstractRequest {

    @NotBlank
    @Length(max = 100, message = "Specified name is too long. Max length is 100")
    private String name;

    @Length(max = 500, message = "Specified bio is too long. Max length is 500")
    private String bio;

}
