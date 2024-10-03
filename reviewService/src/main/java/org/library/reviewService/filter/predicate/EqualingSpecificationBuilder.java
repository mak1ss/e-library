package org.library.reviewService.filter.predicate;

import org.library.reviewService.filter.FilteringOperation;
import org.library.reviewService.filter.SearchCriteria;
import org.springframework.data.mongodb.core.query.Criteria;

import java.util.List;

public class EqualingSpecificationBuilder implements SpecificationBuilder {

    public static final List<FilteringOperation> SUPPORTED_OPERATORS = List.of(
            FilteringOperation.EQUAL,
            FilteringOperation.NOT_EQUAL
    );

    @Override
    public Criteria build(SearchCriteria searchCriteria) {
        return new EqualingSpecification(searchCriteria).toPredicate();
    }
}
