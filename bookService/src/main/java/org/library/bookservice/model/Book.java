package org.library.bookservice.model;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import lombok.Data;
import org.library.bookservice.model.base.Archivable;
import org.library.bookservice.model.base.Identifiable;

@Data
@Entity
public class Book implements Identifiable, Archivable {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;
    private String title;

    private boolean archived;
}
