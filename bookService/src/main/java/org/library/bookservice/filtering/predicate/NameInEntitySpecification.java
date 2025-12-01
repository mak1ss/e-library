package org.library.bookservice.filtering.predicate;

import jakarta.persistence.criteria.CriteriaBuilder;
import jakarta.persistence.criteria.CriteriaQuery;
import jakarta.persistence.criteria.Path;
import jakarta.persistence.criteria.Predicate;
import jakarta.persistence.criteria.Root;
import lombok.AllArgsConstructor;
import org.library.bookservice.filtering.SearchCriteria;
import org.springframework.data.jpa.domain.Specification;

import java.util.List;

@AllArgsConstructor
public class NameInEntitySpecification<EntityType> implements Specification<EntityType> {

    private SearchCriteria searchCriteria;

    @Override
    public Predicate toPredicate(Root<EntityType> root, CriteriaQuery<?> query, CriteriaBuilder cb){
        Path<String> namePath = root.get(searchCriteria.getKey()).get("name");
        switch (searchCriteria.getOperation()){
            case EQUAL -> {
                return cb.equal(namePath, searchCriteria.getValue());
            }
            case CONTAIN -> {
                return cb.like(namePath, "%" + searchCriteria.getValue().toString() + "%");
            }
            case IN -> {
                if(searchCriteria.getValue() instanceof List<?> list){
                    return namePath.in(list);
                }

                return cb.equal(namePath, searchCriteria.getValue());
            }
        }

        return cb.conjunction();
    }
}
