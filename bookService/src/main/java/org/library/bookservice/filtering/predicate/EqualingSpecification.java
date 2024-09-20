package org.library.bookservice.filtering.predicate;

import jakarta.persistence.criteria.CriteriaBuilder;
import jakarta.persistence.criteria.CriteriaQuery;
import jakarta.persistence.criteria.Predicate;
import jakarta.persistence.criteria.Root;
import lombok.AllArgsConstructor;
import org.library.bookservice.filtering.SearchCriteria;
import org.springframework.data.jpa.domain.Specification;

@AllArgsConstructor
public class EqualingSpecification<EntityType> implements Specification<EntityType> {

    private SearchCriteria criteria;

    @Override
    public Predicate toPredicate(Root<EntityType> root, CriteriaQuery<?> query, CriteriaBuilder cb) {

        switch(criteria.getOperation()) {
            case EQUAL -> {
                return cb.equal(root.get(criteria.getKey()), criteria.getValue());
            }
            case NOT_EQUAL -> {
                return cb.notEqual(root.get(criteria.getKey()), criteria.getValue());
            }
            case CONTAIN -> {
                var lowerCaseKey = cb.lower(root.get(criteria.getKey()));
                String lowerCaseValue = ((String) criteria.getValue()).toLowerCase();
                return cb.like(lowerCaseKey, "%" + lowerCaseValue + "%");
            }
        }

        return cb.conjunction();
    }
}
