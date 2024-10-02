package org.library.reviewService.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class PageResponse<ResponseType> {

    private int size;
    private int total;
    private int pageNumber;
    private List<ResponseType> items;

}
