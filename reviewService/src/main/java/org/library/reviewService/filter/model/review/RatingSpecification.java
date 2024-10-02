package org.library.reviewService.filter.model.review;

import lombok.AllArgsConstructor;
import org.library.reviewService.filter.CriteriaBuilder;
import org.library.reviewService.filter.SearchCriteria;
import org.springframework.data.mongodb.core.query.Criteria;

@AllArgsConstructor
public class RatingSpecification implements CriteriaBuilder {

    private SearchCriteria criteria;

    @Override
    public Criteria toPredicate() {
        return switch (criteria.getOperation()) {
            case EQUAL -> Criteria.where(criteria.getKey()).is(criteria.getValue());
            case NOT_EQUAL -> Criteria.where(criteria.getKey()).ne(criteria.getValue());
            case GREATER_THEN -> Criteria.where(criteria.getKey()).gt(criteria.getValue());
            case GREATER_OR_EQUAL -> Criteria.where(criteria.getKey()).gte(criteria.getValue());
            case LESS_THEN -> Criteria.where(criteria.getKey()).lt(criteria.getValue());
            case LESS_OR_EQUAL -> Criteria.where(criteria.getKey()).lte(criteria.getValue());
            default -> new Criteria();
        };
    }
}
