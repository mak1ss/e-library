package org.library.bookservice.dto.bookGenre;

import jakarta.validation.constraints.NotNull;
import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;
import org.library.bookservice.dto.AbstractRequest;

@EqualsAndHashCode(callSuper = true)
@Builder
@Data
public class BookGenreRequest extends AbstractRequest {

    @NotNull
    private Integer genreId;
}
