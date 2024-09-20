package org.library.bookservice.dto.publisher;

import jakarta.validation.constraints.NotBlank;
import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;
import org.hibernate.validator.constraints.Length;
import org.library.bookservice.dto.AbstractRequest;

@EqualsAndHashCode(callSuper = true)
@Builder
@Data
public class PublisherRequest extends AbstractRequest {

    @NotBlank
    @Length(max = 255, message = "Specified name is too long. Max length is 255")
    private String name;

    @NotBlank
    @Length(max = 255, message = "Specified address is too long. Max length is 255")
    private String address;
}
