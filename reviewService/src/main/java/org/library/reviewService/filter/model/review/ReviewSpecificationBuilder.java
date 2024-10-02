package org.library.reviewService.filter.model.review;

import org.library.reviewService.filter.FilterableProperty;
import org.library.reviewService.filter.model.DocumentFilterSpecificationBuilder;
import org.library.reviewService.filter.predicate.DateSpecificationBuilder;
import org.library.reviewService.filter.predicate.EqualingSpecificationBuilder;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class ReviewSpecificationBuilder implements DocumentFilterSpecificationBuilder {

    private final List<FilterableProperty> filterableProperties = List.of(
            new FilterableProperty("userId", Integer.class, new EqualingSpecificationBuilder(),
                    EqualingSpecificationBuilder.SUPPORTED_OPERATORS),
            new FilterableProperty("bookId", Integer.class, new EqualingSpecificationBuilder(),
                    EqualingSpecificationBuilder.SUPPORTED_OPERATORS),
            new FilterableProperty("createdAt", String.class, new DateSpecificationBuilder(),
                    DateSpecificationBuilder.SUPPORTED_OPERATORS),
            new FilterableProperty("rating", Integer.class, new RatingSpecificationBuilder(),
                    RatingSpecificationBuilder.SUPPORTED_OPERATORS)
            );

    @Override
    public List<FilterableProperty> getFilterableProperties() {
        return filterableProperties;
    }
}
