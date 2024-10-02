package org.library.reviewService.filter.predicate;

import org.library.reviewService.filter.SearchCriteria;
import org.springframework.data.mongodb.core.query.Criteria;

public interface SpecificationBuilder {

    Criteria build(SearchCriteria searchCriteria);
}
