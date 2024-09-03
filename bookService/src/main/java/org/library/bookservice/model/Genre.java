package org.library.bookservice.model;

import jakarta.persistence.*;
import lombok.Data;
import org.library.bookservice.model.base.Archivable;
import org.library.bookservice.model.base.Identifiable;

@Data
@Entity
public class Genre implements Identifiable, Archivable {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    private String name;

    @Column(nullable = false, columnDefinition = "TINYINT(1)")
    private boolean archived;
}
