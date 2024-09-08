package org.library.bookservice.filtering;

import lombok.AllArgsConstructor;
import lombok.Data;
import org.library.bookservice.filtering.predicate.SpecificationBuilder;

import java.util.List;

@Data
@AllArgsConstructor
public class FilterableProperty<EntityType> {

    private String propertyName;

    private Class<?> expectedType;

    private SpecificationBuilder<EntityType> specificationBuilder;

    private List<FilteringOperation> supportedOperations;

}
