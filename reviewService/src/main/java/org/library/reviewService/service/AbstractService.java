package org.library.reviewService.service;

import org.library.reviewService.model.base.Identifiable;
import org.library.reviewService.repository.BaseRepository;
import org.springframework.data.domain.Pageable;
import org.springframework.data.mongodb.core.MongoOperations;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

@Service
public abstract class AbstractService<T extends Identifiable> {

    protected abstract BaseRepository<T> getRepository();

    protected abstract MongoOperations getMongoOperations();

    protected abstract Class<T> getEntityClass();

    public List<T> getAll(Pageable pageable) {
        return getRepository().findAll(pageable).getContent();
    }

    public Optional<List<T>> getAllByQuery(Query query) {
        return Optional.of(getMongoOperations().find(query, getEntityClass()));
    }

    public Optional<T> getById(String id) {
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

    public void delete(T entity) {
        beforeDelete(entity);

        getRepository().save(entity);
    }

    protected void beforeDelete(T entity) {
    }

    public void deleteById(String id) {
        getRepository().deleteById(id);
    }
}
