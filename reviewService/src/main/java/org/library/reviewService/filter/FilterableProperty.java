package org.library.reviewService.filter;

import lombok.AllArgsConstructor;
import lombok.Data;
import org.library.reviewService.filter.predicate.SpecificationBuilder;

import java.util.List;

@Data
@AllArgsConstructor
public class FilterableProperty {

    private String propertyName;

    private Class<?> expectedType;

    private SpecificationBuilder specificationBuilder;

    private List<FilteringOperation> supportedOperations;

}
