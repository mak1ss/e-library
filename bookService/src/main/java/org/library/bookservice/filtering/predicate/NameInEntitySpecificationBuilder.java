package org.library.bookservice.filtering.predicate;

import org.library.bookservice.filtering.FilteringOperation;
import org.library.bookservice.filtering.SearchCriteria;
import org.springframework.data.jpa.domain.Specification;

import java.util.List;

public class NameInEntitySpecificationBuilder<EntityType> implements SpecificationBuilder<EntityType>{

    public static final List<FilteringOperation> SUPPORTED_OPERATORS = List.of(
            FilteringOperation.EQUAL,
            FilteringOperation.CONTAIN
    );

    @Override
    public Specification<EntityType> build(SearchCriteria searchCriteria) {
        return new NameInEntitySpecification<>(searchCriteria);
    }
}
