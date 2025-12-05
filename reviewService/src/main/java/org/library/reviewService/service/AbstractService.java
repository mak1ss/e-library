package org.library.reviewService.service;

import org.library.reviewService.filter.ArchivedSpecification;
import org.library.reviewService.model.base.Archivable;
import org.library.reviewService.model.base.Identifiable;
import org.library.reviewService.repository.BaseRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.mongodb.core.MongoOperations;
import org.springframework.data.mongodb.core.query.Criteria;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.data.mongodb.core.query.Update;
import org.springframework.data.support.PageableExecutionUtils;
import org.springframework.stereotype.Service;

import java.util.Optional;

@Service
public abstract class AbstractService<DocumentType extends Identifiable> {

    protected abstract BaseRepository<DocumentType> getRepository();

    protected abstract MongoOperations getMongoOperations();

    protected abstract Class<DocumentType> getEntityClass();

    public Page<DocumentType> getAll(Pageable pageable) {
        return getRepository().findAll(pageable);
    }

    public Page<DocumentType> getAll(Query query, Pageable pageable) {
        return getAll(query, pageable, false);
    }

    public Page<DocumentType> getAll(Query query, Pageable pageable, boolean includeArchived) {
        return PageableExecutionUtils.getPage(getMongoOperations()
                .find(query.with(pageable)
                    .addCriteria(addArchivedCriteria(includeArchived))
                    .addCriteria(addAdditionalCriteriaForGetAll()), getEntityClass()),
            pageable,
            () -> getMongoOperations().count(Query.of(query).limit(-1).skip(-1), getEntityClass()));
    }

    protected Criteria addArchivedCriteria(boolean includeArchived) {
        return !includeArchived ? new ArchivedSpecification().toPredicate() : new Criteria();
    }

    protected Criteria addAdditionalCriteriaForGetAll() {
        return new Criteria();
    }

    public Optional<DocumentType> getById(String id) {
        return getRepository().findById(id);
    }

    public Optional<DocumentType> getOne(Query query) {
        return getOneDocumentByQuery(query, true);
    }

    public Optional<DocumentType> getOne(Query query, boolean includeArchived) {
        return getOneDocumentByQuery(query, includeArchived);
    }

    private Optional<DocumentType> getOneDocumentByQuery(Query query, boolean includeArchived) {
        return Optional.ofNullable(getMongoOperations()
            .findOne(query.addCriteria(addArchivedCriteria(includeArchived)), getEntityClass()));
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

        if (entity instanceof Archivable archivable) {
            archivable.setArchived(true);
            getRepository().save(entity);
        } else {
            delete(entity, true);
        }
    }

    public void delete(DocumentType entity, boolean ignorePermissions) {
        if (!ignorePermissions) {
            delete(entity);
        } else {
            getRepository().deleteById(entity.getId());
        }
    }

    protected void beforeDelete(DocumentType entity) {
    }

    protected void afterDelete(DocumentType entity) {
    }

    public void deleteById(String id) {
        DocumentType entity = getRepository().findById(id).orElseThrow();

        beforeDelete(entity);

        if (entity instanceof Archivable archivable) {
            archivable.setArchived(true);
            getRepository().save(entity);
        } else {
            deleteById(id, true);
        }

        afterDelete(entity);
    }

    public void deleteById(String id, boolean ignorePermissions) {
        if (!ignorePermissions) {
            deleteById(id);
        } else {
            getRepository().deleteById(id);
        }
    }

    public void deleteByQuery(Query query) {
        if (getEntityClass().isAssignableFrom(Archivable.class)) {
            Update update = new Update();
            update.set("archived", true);
            getMongoOperations().updateMulti(query, update, getEntityClass());
        } else {
            getMongoOperations().remove(query, getEntityClass());
        }
    }
}
