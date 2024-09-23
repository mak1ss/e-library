package org.library.bookservice.dto.genre;

import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;
import org.library.bookservice.dto.AbstractResponse;

@EqualsAndHashCode(callSuper = true)
@Builder
@Data
public class GenreResponse extends AbstractResponse {

    private Integer id;

    private String name;

    private String description;
}
