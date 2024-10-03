package org.library.reviewService.repository;

import org.library.reviewService.model.base.Identifiable;
import org.springframework.data.repository.NoRepositoryBean;

@NoRepositoryBean
public interface BaseRepository<T extends Identifiable> extends PrimaryRepository<T, String> {
}
