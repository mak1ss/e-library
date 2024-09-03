package org.library.bookservice.model;

import jakarta.persistence.*;
import lombok.Data;
import org.library.bookservice.model.base.Archivable;
import org.library.bookservice.model.base.Identifiable;

import java.time.LocalDate;

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

    @Column(nullable = false, precision = 10, scale = 2)
    private Double price;

    @Column(nullable = false, columnDefinition = "TINYINT(1)")
    private boolean archived;
}