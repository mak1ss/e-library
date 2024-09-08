package org.library.bookservice.filtering.predicate;

import org.library.bookservice.filtering.SearchCriteria;
import org.springframework.data.jpa.domain.Specification;

public interface SpecificationBuilder<EntityType> {

    Specification<EntityType> build(SearchCriteria searchCriteria);
}
