package org.library.reviewService.filter.predicate;

import lombok.AllArgsConstructor;
import org.library.reviewService.filter.CriteriaBuilder;
import org.library.reviewService.filter.SearchCriteria;
import org.springframework.data.mongodb.core.query.Criteria;

@AllArgsConstructor
public class EqualingSpecification implements CriteriaBuilder {

    private SearchCriteria criteria;

    @Override
    public Criteria toPredicate() {
        switch (criteria.getOperation()) {
            case EQUAL -> {
                return Criteria.where(criteria.getKey()).is(criteria.getValue());
            }
            case NOT_EQUAL -> {
                return Criteria.where(criteria.getKey()).ne(criteria.getValue());
            }
        }

        return new Criteria();
    }
}
