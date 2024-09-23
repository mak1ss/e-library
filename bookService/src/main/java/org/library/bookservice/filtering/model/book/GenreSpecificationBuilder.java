package org.library.bookservice.filtering.model.book;

import org.library.bookservice.filtering.FilteringOperation;
import org.library.bookservice.filtering.SearchCriteria;
import org.library.bookservice.filtering.predicate.SpecificationBuilder;
import org.library.bookservice.model.Book;
import org.springframework.data.jpa.domain.Specification;

import java.util.List;

public class GenreSpecificationBuilder implements SpecificationBuilder<Book> {

    public static final List<FilteringOperation> SUPPORTED_OPERATORS = List.of(
            FilteringOperation.IN,
            FilteringOperation.CONTAIN
    );

    @Override
    public Specification<Book> build(SearchCriteria searchCriteria) {
        return new GenreSpecification(searchCriteria);
    }
}
