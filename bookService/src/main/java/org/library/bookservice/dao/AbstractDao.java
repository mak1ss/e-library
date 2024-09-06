package org.library.bookservice.dao;

import org.library.bookservice.filtering.ArchivedSpecification;
import org.library.bookservice.model.base.Archivable;
import org.library.bookservice.model.base.PrimaryEntity;
import org.library.bookservice.repository.PrimaryRepository;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.domain.Specification;

import java.util.List;
import java.util.Optional;

public abstract class AbstractDao<T extends PrimaryEntity<Integer>> {

    protected abstract PrimaryRepository<Integer, T> getRepository();

    public List<T> getAll(Pageable pageable) {
        return getAll(pageable, false);
    }

    public List<T> getAll(Pageable pageable, boolean includeArchived) {
        return getRepository().findAll(
                addSpecification(includeArchived)
                .and(addAdditionalSpecificationForGetAll()), pageable).getContent();
    }

    public List<T> getAll(Pageable pageable, Specification<T> filter) {
        return getAll(pageable, filter, false);
    }

    public List<T> getAll(Pageable pageable, Specification<T> filter, boolean includeArchived) {
        return getRepository().findAll(
                addSpecification(includeArchived)
                .and(filter)
                .and(addAdditionalSpecificationForGetAll()), pageable).getContent();
    }

    protected Specification<T> addSpecification(boolean includeArchived) {
        Specification<T> spec = Specification.where(null);
        if (!includeArchived) {
            spec = spec.and(new ArchivedSpecification<>());
        }

        return spec;
    }

    protected Specification<T> addAdditionalSpecificationForGetAll() {
        return Specification.where(null);
    }

    public Optional<T> getOne(Specification<T> filter) {
        return getRepository().findOne(filter);
    }

    public Optional<T> getById(Integer id) {
        return getRepository().findById(id);
    }

    public T create(T entity) {
        beforeCreate();
        return getRepository().save(entity);
    }

    protected void beforeCreate() {
    }

    public T update(T entity) {
        beforeUpdate(entity);
        return getRepository().save(entity);
    }

    protected void beforeUpdate(T entity) {
    }

    public T update(T entity, boolean ignorePermissions) {
        if (!ignorePermissions) {
            return update(entity);
        }
        return getRepository().save(entity);
    }

    public void delete(T entity) {
        beforeDelete(entity);
        if (entity instanceof Archivable archivable) {
            archivable.setArchived(true);
            getRepository().save(entity);
        } else {
            delete(entity, true);
        }
    }

    protected void beforeDelete(T entity) {
    }

    public void delete(T entity, boolean ignorePermissions) {
        if (!ignorePermissions) {
            delete(entity);
        } else {
            getRepository().deleteById(entity.getId());
        }
    }

    public void deleteById(Integer id) {
        T entity = getRepository().findById(id).orElseThrow();
        if (entity instanceof Archivable archivable) {
            archivable.setArchived(true);
            getRepository().save(entity);
        } else {
            deleteById(id, true);
        }
    }

    public void deleteById(Integer id, boolean ignorePermissions) {
        if (!ignorePermissions) {
            deleteById(id);
        } else {
            getRepository().deleteById(id);
        }
    }


}
