package org.library.reviewService.filter;

import org.springframework.data.mongodb.core.query.Criteria;

public interface CriteriaBuilder {

    Criteria toPredicate();
}
