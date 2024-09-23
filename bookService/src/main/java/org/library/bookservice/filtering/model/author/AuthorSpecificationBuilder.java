package org.library.bookservice.filtering.model.author;

import org.library.bookservice.filtering.FilterableProperty;
import org.library.bookservice.filtering.model.EntityFilterSpecificationBuilder;
import org.library.bookservice.filtering.predicate.EqualingSpecificationBuilder;
import org.library.bookservice.model.Author;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class AuthorSpecificationBuilder implements EntityFilterSpecificationBuilder<Author> {

    private final List<FilterableProperty<Author>> FILTERABLE_PROPERTIES = List.of(
            new FilterableProperty<>("name", String.class, new EqualingSpecificationBuilder<>(),
                    EqualingSpecificationBuilder.SUPPORTED_OPERATORS)
    );

    @Override
    public List<FilterableProperty<Author>> getFilterableProperties() {
        return FILTERABLE_PROPERTIES;
    }
}
