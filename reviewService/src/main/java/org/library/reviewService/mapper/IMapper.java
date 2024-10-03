package org.library.reviewService.mapper;

import org.library.reviewService.dto.AbstractRequest;
import org.library.reviewService.dto.AbstractResponse;
import org.library.reviewService.model.base.Identifiable;

import java.util.List;
import java.util.Optional;

public interface IMapper<T extends Identifiable, RequestType extends AbstractRequest, ResponseType extends AbstractResponse> {

    T requestToEntity(Optional<String> id, RequestType request);

    ResponseType entityToResponse(T entity);

    List<ResponseType> entityToResponseList(List<T> entityList);
}
