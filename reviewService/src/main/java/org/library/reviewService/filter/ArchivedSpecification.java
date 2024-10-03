package org.library.reviewService.filter;

import org.springframework.data.mongodb.core.query.Criteria;

public class ArchivedSpecification implements CriteriaBuilder{

    @Override
    public Criteria toPredicate() {
        return Criteria.where("archived").is(false);
    }
}
