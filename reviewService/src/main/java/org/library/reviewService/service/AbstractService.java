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
public abstract class AbstractService<DocumentType extends Identifiable> {

    protected abstract BaseRepository<DocumentType> getRepository();

    protected abstract MongoOperations getMongoOperations();

    protected abstract Class<DocumentType> getEntityClass();

    public List<DocumentType> getAll(Pageable pageable) {
        return getRepository().findAll(pageable).getContent();
    }

    public Optional<List<DocumentType>> getAllByQuery(Query query) {
        return Optional.of(getMongoOperations().find(query, getEntityClass()));
    }

    public Optional<DocumentType> getById(String id) {
        return getRepository().findById(id);
    }

    public Optional<DocumentType> getOne(Query query) {
        return Optional.ofNullable(getMongoOperations().findOne(query, getEntityClass()));
    }

    public DocumentType create(DocumentType entity) {
        beforeCreate(entity);
        entity = getRepository().save(entity);
        afterCreate(entity);
        return entity;
    }

    protected void beforeCreate(DocumentType entity) {
    }

    protected void afterCreate(DocumentType entity) {
    }

    public DocumentType update(DocumentType entity) {
        beforeUpdate(entity);
        return getRepository().save(entity);
    }

    protected void beforeUpdate(DocumentType entity) {
    }

    public void delete(DocumentType entity) {
        beforeDelete(entity);

        getRepository().save(entity);
    }

    protected void beforeDelete(DocumentType entity) {
    }

    public void deleteById(String id) {
        getRepository().deleteById(id);
    }
}
