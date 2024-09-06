package org.library.bookservice.dto.publisher;

import lombok.Builder;
import lombok.Data;
import lombok.EqualsAndHashCode;
import org.library.bookservice.dto.AbstractResponse;

@EqualsAndHashCode(callSuper = true)
@Builder
@Data
public class PublisherResponse extends AbstractResponse {

    private Integer id;

    private String name;
}
