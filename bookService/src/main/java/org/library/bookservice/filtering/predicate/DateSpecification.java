package org.library.bookservice.filtering.predicate;

import jakarta.persistence.criteria.CriteriaBuilder;
import jakarta.persistence.criteria.CriteriaQuery;
import jakarta.persistence.criteria.Predicate;
import jakarta.persistence.criteria.Root;
import lombok.AllArgsConstructor;
import org.library.bookservice.filtering.SearchCriteria;
import org.springframework.data.jpa.domain.Specification;

import java.time.LocalDateTime;

@AllArgsConstructor
public class DateSpecification<EntityType> implements Specification<EntityType> {

    private SearchCriteria criteria;

    @Override
    public Predicate toPredicate(Root<EntityType> root, CriteriaQuery<?> query, CriteriaBuilder cb) {
        LocalDateTime criteriaDate = LocalDateTime.parse(criteria.getValue()+"T00:00:00");
        switch(criteria.getOperation()) {
            case EQUAL -> {
                return handleCriteriaEqual(root, cb, criteriaDate);
            }
            case NOT_EQUAL -> {
                return cb.not(handleCriteriaEqual(root, cb, criteriaDate));
            }
            case GREATER_THEN -> {
                return cb.greaterThan(root.get(criteria.getKey()), toEndOfDay(criteriaDate));
            }
            case GREATER_OR_EQUAL -> {
                return cb.or(
                        cb.greaterThan(root.get(criteria.getKey()), criteriaDate),
                        handleCriteriaEqual(root, cb, criteriaDate)
                );
            }
            case LESS_THEN -> {
                return cb.lessThan(root.get(criteria.getKey()), criteriaDate);
            }
            case LESS_OR_EQUAL -> {
                return cb.or(
                        cb.lessThan(root.get(criteria.getKey()), criteriaDate),
                        handleCriteriaEqual(root, cb, criteriaDate)
                );
            }
        }

        return cb.conjunction();
    }

    private Predicate handleCriteriaEqual(Root<EntityType> root, CriteriaBuilder cb, LocalDateTime value) {
        LocalDateTime startOfDay = value.toLocalDate().atStartOfDay();
        LocalDateTime endOfDay = toEndOfDay(value);

        return cb.and(
                cb.greaterThanOrEqualTo(root.get(criteria.getKey()), startOfDay),
                cb.lessThanOrEqualTo(root.get(criteria.getKey()), endOfDay)
        );
    }

    private LocalDateTime toEndOfDay(LocalDateTime date) {
        return date.toLocalDate().atTime(23, 59, 59);
    }
}
