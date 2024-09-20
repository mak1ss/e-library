package org.library.bookservice.filtering.model.book;

import org.library.bookservice.filtering.FilteringOperation;
import org.library.bookservice.filtering.SearchCriteria;
import org.library.bookservice.filtering.predicate.SpecificationBuilder;
import org.springframework.data.jpa.domain.Specification;

import java.util.List;


public class PriceSpecificationBuilder<EntityType> implements SpecificationBuilder<EntityType> {

    public static final List<FilteringOperation> SUPPORTED_OPERATORS = List.of(
            FilteringOperation.EQUAL,
            FilteringOperation.GREATER_OR_EQUAL,
            FilteringOperation.LESS_OR_EQUAL
    );

    @Override
    public Specification<EntityType> build(SearchCriteria searchCriteria) {
        return new PriceSpecification<>(searchCriteria);
    }
}
