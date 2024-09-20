package org.library.bookservice.filtering.model.book;

import jakarta.persistence.criteria.CriteriaBuilder;
import jakarta.persistence.criteria.CriteriaQuery;
import jakarta.persistence.criteria.Predicate;
import jakarta.persistence.criteria.Root;
import lombok.AllArgsConstructor;
import org.library.bookservice.filtering.SearchCriteria;
import org.springframework.data.jpa.domain.Specification;

@AllArgsConstructor
public class PriceSpecification<EntityType> implements Specification<EntityType> {

    private SearchCriteria criteria;


    @Override
    public Predicate toPredicate(Root<EntityType> root, CriteriaQuery<?> query, CriteriaBuilder cb) {
        Double criteriaValue = (Double) criteria.getValue();
        switch (criteria.getOperation()) {
            case EQUAL -> {
                return cb.equal(root.get(criteria.getKey()), criteriaValue);
            }
            case GREATER_OR_EQUAL -> {
                return cb.ge(root.get(criteria.getKey()), criteriaValue);
            }
            case LESS_OR_EQUAL -> {
                return cb.le(root.get(criteria.getKey()), criteriaValue);
            }
        }
        return cb.conjunction();
    }
}
