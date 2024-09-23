package org.library.bookservice.filtering.predicate;

import org.library.bookservice.filtering.FilteringOperation;
import org.library.bookservice.filtering.SearchCriteria;
import org.springframework.data.jpa.domain.Specification;

import java.util.List;

public class DateSpecificationBuilder<EntityType> implements SpecificationBuilder<EntityType> {

    public static final List<FilteringOperation> SUPPORTED_OPERATORS = List.of(
            FilteringOperation.EQUAL,
            FilteringOperation.NOT_EQUAL,
            FilteringOperation.GREATER_THEN,
            FilteringOperation.GREATER_OR_EQUAL,
            FilteringOperation.LESS_THEN,
            FilteringOperation.LESS_OR_EQUAL
    );

    @Override
    public Specification<EntityType> build(SearchCriteria searchCriteria) {
        return new DateSpecification<>(searchCriteria);
    }
}
