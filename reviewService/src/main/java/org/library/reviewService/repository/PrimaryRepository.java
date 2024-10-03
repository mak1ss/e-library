package org.library.reviewService.repository;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.repository.NoRepositoryBean;

@NoRepositoryBean
public interface PrimaryRepository<T, TID> extends MongoRepository<T, TID> {
}
