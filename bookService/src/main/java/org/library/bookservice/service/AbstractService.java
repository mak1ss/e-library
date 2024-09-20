package org.library.bookservice.service;

import org.library.bookservice.dao.AbstractDao;
import org.library.bookservice.model.base.Identifiable;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

public abstract class AbstractService<T extends Identifiable> {

    protected abstract AbstractDao<T> getDao();


    public List<T> getAll(Pageable pageable) {
        return getDao().getAll(pageable);
    }

    public Page<T> getAll(Pageable pageable, Specification<T> filter) {
        return getDao().getAll(pageable, filter);
    }

    public Optional<T> getById(Integer id) {
        return getDao().getById(id);
    }

    public T save(T entity) {
        return getDao().create(entity);
    }

    public T update(T entity) {
        return update(entity, false);
    }

    @Transactional
    public T update( T entity, boolean ignorePermissions ) {
        beforeUpdate(entity);
        entity = getDao().update( entity, ignorePermissions );
        afterUpdate(entity);
        return entity;
    }

    protected void beforeUpdate(T entity) {}

    protected void afterUpdate(T entity) {}

    public void delete(T entity) {
        getDao().delete(entity);
    }

    private void delete(T entity, boolean ignorePermissions) {
        beforeDelete(entity);
        getDao().delete(entity, ignorePermissions);
        afterDelete(entity);
    }

    protected void beforeDelete(T entity) {
    }

    protected void afterDelete(T entity) {
    }

    public void deleteById(Integer id) {
        getDao().deleteById(id);
    }

    @Transactional
    public void deleteById(Integer id, boolean ignorePermissions) {
        T entity = getDao().getById(id).orElseThrow();
        delete(entity, ignorePermissions);
    }
}
