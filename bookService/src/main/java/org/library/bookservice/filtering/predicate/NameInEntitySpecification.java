package org.library.bookservice.filtering.predicate;

import jakarta.persistence.criteria.CriteriaBuilder;
import jakarta.persistence.criteria.CriteriaQuery;
import jakarta.persistence.criteria.Predicate;
import jakarta.persistence.criteria.Root;
import lombok.AllArgsConstructor;
import org.library.bookservice.filtering.SearchCriteria;
import org.springframework.data.jpa.domain.Specification;

@AllArgsConstructor
public class NameInEntitySpecification<EntityType> implements Specification<EntityType> {

    private SearchCriteria searchCriteria;

    @Override
    public Predicate toPredicate(Root<EntityType> root, CriteriaQuery<?> query, CriteriaBuilder cb){

        switch (searchCriteria.getOperation()){
            case EQUAL -> {
                return cb.equal(root.get(searchCriteria.getKey()).get("name"), searchCriteria.getValue());
            }
            case CONTAIN -> {
                return cb.like(root.get(searchCriteria.getKey()).get("name"), "%" + searchCriteria.getValue().toString() + "%");
            }
        }

        return cb.conjunction();
    }
}
