package org.library.bookservice.mapper;

import org.library.bookservice.dto.AbstractRequest;
import org.library.bookservice.dto.AbstractResponse;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

public interface Mapper<T, ResponseType extends AbstractResponse, RequestType extends AbstractRequest> {

    T requestToEntity(RequestType request, Optional<Integer> id);

    ResponseType entityToResponse(T entity);

    List<ResponseType> entitiesToListResponse(Collection<T> entityList);

}
