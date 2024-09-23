package org.library.bookservice.repository;

import org.library.bookservice.model.base.PrimaryEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.repository.NoRepositoryBean;
import org.springframework.data.repository.PagingAndSortingRepository;

@NoRepositoryBean
public interface PrimaryRepository<IdType, EntityType extends PrimaryEntity<IdType>> extends JpaRepository<EntityType, IdType>,
        PagingAndSortingRepository<EntityType, IdType>, JpaSpecificationExecutor<EntityType> {

}
