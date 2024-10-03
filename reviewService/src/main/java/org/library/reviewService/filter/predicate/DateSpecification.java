package org.library.reviewService.filter.predicate;

import lombok.AllArgsConstructor;
import org.library.reviewService.filter.CriteriaBuilder;
import org.library.reviewService.filter.SearchCriteria;
import org.springframework.data.mongodb.core.query.Criteria;

import java.time.LocalDateTime;

@AllArgsConstructor
public class DateSpecification implements CriteriaBuilder {

    private SearchCriteria criteria;

    @Override
    public Criteria toPredicate() {
        LocalDateTime criteriaDate = LocalDateTime.parse(criteria.getValue() + "T00:00:00");
        return switch (criteria.getOperation()) {
            case EQUAL -> handleCriteriaEqual(criteriaDate);
            case NOT_EQUAL -> handleCriteriaEqual(criteriaDate).not();
            case GREATER_THEN -> Criteria.where(criteria.getKey()).gt(criteriaDate);
            case GREATER_OR_EQUAL -> Criteria.where(criteria.getKey()).gte(criteriaDate);
            case LESS_THEN -> Criteria.where(criteria.getKey()).lt(criteriaDate);
            case LESS_OR_EQUAL -> Criteria.where(criteria.getKey()).lte(criteriaDate);
            default -> new Criteria();
        };
    }

    private Criteria handleCriteriaEqual(LocalDateTime value) {
        LocalDateTime startOfDay = value.toLocalDate().atStartOfDay();
        LocalDateTime endOfDay = toEndOfDay(value);

        return Criteria.where(criteria.getKey()).gte(startOfDay).lt(endOfDay);
    }

    private LocalDateTime toEndOfDay(LocalDateTime date) {
        return date.toLocalDate().atTime(23, 59, 59);
    }
}
