package org.library.reviewService.filter.model;


import org.library.reviewService.filter.FilterableProperty;
import org.library.reviewService.filter.SearchCriteria;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.data.mongodb.core.query.Query;

import java.util.List;
import java.util.Optional;

public interface DocumentFilterSpecificationBuilder {

    Logger LOG = LoggerFactory.getLogger(DocumentFilterSpecificationBuilder.class);

    List<FilterableProperty> getFilterableProperties();

    default Query buildSpecification(List<SearchCriteria> criteriaList) {
        Query query = new Query();

        for (SearchCriteria criteria : criteriaList) {
            Optional<FilterableProperty> property = getFilterableProperties().stream()
                    .filter(p -> p.getPropertyName().equals(criteria.getKey()))
                    .findFirst();

            if(property.isPresent()) {
                query.addCriteria(property.get().getSpecificationBuilder().build(criteria));
            } else {
                LOG.warn("[{}] is unsupported property, filtering skipped", criteria.getKey());
            }
        }

        return query;
    }
}
