package org.library.bookservice.filtering.model.book;

import jakarta.persistence.criteria.*;
import lombok.AllArgsConstructor;
import org.library.bookservice.filtering.SearchCriteria;
import org.library.bookservice.model.Book;
import org.library.bookservice.model.Genre;
import org.springframework.data.jpa.domain.Specification;

import java.util.List;

@AllArgsConstructor
public class GenreSpecification implements Specification<Book> {

    private final SearchCriteria criteria;

    @Override
    public Predicate toPredicate(Root<Book> root, CriteriaQuery<?> query, CriteriaBuilder cb) {
        Join<Book, Genre> bookGenre = root.join("genres", JoinType.INNER);
        List<String> criteriaGenres = criteria.getValue() instanceof List
                ? (List<String>) criteria.getValue()
                : List.of((String) criteria.getValue());
        switch (criteria.getOperation()) {
            case IN -> {
                return bookGenre.get("name").in(criteriaGenres);
            }
            case CONTAIN -> {
                return cb.like(bookGenre.get("name"), "%" + criteria.getValue() + "%");
            }
        }
        return cb.conjunction();
    }
}
