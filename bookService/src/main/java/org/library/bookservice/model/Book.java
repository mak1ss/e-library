package org.library.bookservice.model;

import jakarta.persistence.*;
import lombok.Data;
import org.library.bookservice.model.base.Archivable;
import org.library.bookservice.model.base.Identifiable;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

@Data
@Entity
public class Book implements Identifiable, Archivable {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
    private String title;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "author_id")
    private Author author;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id")
    private Category category;

    @Column(length = 500)
    private String description;

    @Column(unique = true, length = 20)
    private String ISBN;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "publisher_id")
    private Publisher publisher;

    @Column(name = "release_date")
    private LocalDate releaseDate;

    @Column(nullable = false)
    private Double price;

    @ManyToMany
    @JoinTable(
            name = "book_genre",
            joinColumns = @JoinColumn(name = "book_id"),
            inverseJoinColumns = @JoinColumn(name = "genre_id")
    )
    private List<Genre> bookGenres = new ArrayList<>();

    @Column(nullable = false, columnDefinition = "TINYINT(1)")
    private boolean archived;
}