package org.library.bookservice.repository;

import org.library.bookservice.model.base.Identifiable;
import org.springframework.data.repository.NoRepositoryBean;

@NoRepositoryBean
public interface BaseCRUDRepository<EntityType extends Identifiable> extends PrimaryRepository<Integer, EntityType> {
}
