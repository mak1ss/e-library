package org.library.reviewService.filter.model.review;

import org.library.reviewService.filter.FilteringOperation;
import org.library.reviewService.filter.SearchCriteria;
import org.library.reviewService.filter.predicate.SpecificationBuilder;
import org.springframework.data.mongodb.core.query.Criteria;

import java.util.List;

public class RatingSpecificationBuilder implements SpecificationBuilder {

    public static final List<FilteringOperation> SUPPORTED_OPERATORS = List.of(
            FilteringOperation.EQUAL,
            FilteringOperation.NOT_EQUAL,
            FilteringOperation.GREATER_THEN,
            FilteringOperation.GREATER_OR_EQUAL,
            FilteringOperation.LESS_THEN,
            FilteringOperation.LESS_OR_EQUAL
    );

    @Override
    public Criteria build(SearchCriteria searchCriteria) {
        return new RatingSpecification(searchCriteria).toPredicate();
    }
}
