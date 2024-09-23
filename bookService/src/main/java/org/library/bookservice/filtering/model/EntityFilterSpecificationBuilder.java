package org.library.bookservice.filtering.model;

import org.library.bookservice.filtering.FilterableProperty;
import org.library.bookservice.filtering.SearchCriteria;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.jpa.domain.Specification;

import java.util.List;
import java.util.Optional;


public interface EntityFilterSpecificationBuilder<EntityType> {

    Logger LOG = LoggerFactory.getLogger(EntityFilterSpecificationBuilder.class);

    List<FilterableProperty<EntityType>> getFilterableProperties();

    default Specification<EntityType> buildSpecification(List<SearchCriteria> criteriaList) {
        Specification<EntityType> spec = Specification.where(null);

        for (SearchCriteria criteria : criteriaList) {
            Optional<FilterableProperty<EntityType>> property = getFilterableProperties().stream()
                    .filter(p -> p.getPropertyName().equals(criteria.getKey())).findFirst();

            if (property.isPresent()) {
                spec = spec.and(property.get().getSpecificationBuilder().build(criteria));
            } else {
                LOG.warn("[{}] is unsupported property, filtering skipped", criteria.getKey());
            }
        }

        return spec;
    }
}
