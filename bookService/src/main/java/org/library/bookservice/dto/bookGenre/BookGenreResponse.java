package org.library.bookservice.dto.bookGenre;

import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;
import org.library.bookservice.dto.AbstractResponse;

@EqualsAndHashCode(callSuper = true)
@Builder
@Data
public class BookGenreResponse extends AbstractResponse {

    private Integer id;

    private Integer genreId;
}
