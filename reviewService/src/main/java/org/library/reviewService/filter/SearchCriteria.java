package org.library.reviewService.filter;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class SearchCriteria {

    private String key;

    private FilteringOperation operation;

    private Object value;
}
