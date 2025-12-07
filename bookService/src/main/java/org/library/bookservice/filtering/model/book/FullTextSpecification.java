package org.library.bookservice.filtering.model.book;

import jakarta.persistence.criteria.CriteriaBuilder;
import jakarta.persistence.criteria.CriteriaQuery;
import jakarta.persistence.criteria.Expression;
import jakarta.persistence.criteria.Join;
import jakarta.persistence.criteria.JoinType;
import jakarta.persistence.criteria.Predicate;
import jakarta.persistence.criteria.Root;
import lombok.AllArgsConstructor;
import org.library.bookservice.filtering.SearchCriteria;
import org.library.bookservice.model.Book;
import org.springframework.data.jpa.domain.Specification;

@AllArgsConstructor
public class FullTextSpecification implements Specification<Book> {

    private final SearchCriteria criteria;

    @Override
    public Predicate toPredicate(Root<Book> root, CriteriaQuery<?> query, CriteriaBuilder cb) {
        String searchTerm = (String) criteria.getValue();
        if (searchTerm == null || searchTerm.isBlank()) {
            return cb.conjunction();
        }

        Expression<Double> matchScore = cb.function("match_3_columns", Double.class,
            root.get("title"),
            root.get("ISBN"),
            root.get("description"),
            cb.literal(searchTerm + "*")
        );

        Predicate fullTextPredicate = cb.greaterThan(matchScore, 0.0);

        Join<Object, Object> authorJoin = root.join("author", JoinType.LEFT);
        Predicate authorPredicate = cb.like(cb.lower(authorJoin.get("name")), "%" + searchTerm.toLowerCase() + "%");

        return cb.or(fullTextPredicate, authorPredicate);
    }
}
