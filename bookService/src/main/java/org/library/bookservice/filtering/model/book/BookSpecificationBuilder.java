package org.library.bookservice.filtering.model.book;

import org.library.bookservice.filtering.FilterableProperty;
import org.library.bookservice.filtering.model.EntityFilterSpecificationBuilder;
import org.library.bookservice.filtering.predicate.DateSpecificationBuilder;
import org.library.bookservice.filtering.predicate.EqualingSpecificationBuilder;
import org.library.bookservice.filtering.predicate.NameInEntitySpecificationBuilder;
import org.library.bookservice.model.Book;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class BookSpecificationBuilder implements EntityFilterSpecificationBuilder<Book> {

    private final List<FilterableProperty<Book>> FILTERABLE_PROPERTIES = List.of(
            new FilterableProperty<>("title", String.class, new EqualingSpecificationBuilder<>(),
                    EqualingSpecificationBuilder.SUPPORTED_OPERATORS),
            new FilterableProperty<>("author", String.class, new NameInEntitySpecificationBuilder<>(),
                    NameInEntitySpecificationBuilder.SUPPORTED_OPERATORS),
            new FilterableProperty<>("category", String.class, new NameInEntitySpecificationBuilder<>(),
                    NameInEntitySpecificationBuilder.SUPPORTED_OPERATORS),
            new FilterableProperty<>("publisher", String.class, new NameInEntitySpecificationBuilder<>(),
                    NameInEntitySpecificationBuilder.SUPPORTED_OPERATORS),
            new FilterableProperty<>("releaseDate", String.class, new DateSpecificationBuilder<>(),
                    DateSpecificationBuilder.SUPPORTED_OPERATORS),
            new FilterableProperty<>("price", Double.class, new PriceSpecificationBuilder<>(),
                    PriceSpecificationBuilder.SUPPORTED_OPERATORS),
            new FilterableProperty<>("genres", String.class, new GenreSpecificationBuilder(),
                    GenreSpecificationBuilder.SUPPORTED_OPERATORS)
    );

    @Override
    public List<FilterableProperty<Book>> getFilterableProperties() {
        return FILTERABLE_PROPERTIES;
    }
}
