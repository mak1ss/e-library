package org.library.bookservice.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class PageResponse<ResponseType> {

    private int size;
    private long total;
    private int pageNumber;
    private List<ResponseType> items;

}
