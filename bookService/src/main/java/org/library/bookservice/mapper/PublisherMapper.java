package org.library.bookservice.mapper;

import org.library.bookservice.dto.publisher.PublisherRequest;
import org.library.bookservice.dto.publisher.PublisherResponse;
import org.library.bookservice.model.Publisher;
import org.springframework.stereotype.Service;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

@Service
public class PublisherMapper implements Mapper<Publisher, PublisherResponse, PublisherRequest> {

    @Override
    public Publisher requestToEntity(PublisherRequest request, Optional<Integer> id) {
        Publisher entity = new Publisher();

        entity.setId(id.orElse(null));
        entity.setName(request.getName());
        entity.setAddress(request.getAddress());

        return entity;
    }

    @Override
    public PublisherResponse entityToResponse(Publisher entity) {
        return PublisherResponse.builder()
                .id(entity.getId())
                .name(entity.getName())
                .address(entity.getAddress())
                .build();
    }

    @Override
    public List<PublisherResponse> entitiesToListResponse(Collection<Publisher> entityList) {
        return entityList.stream().map(this::entityToResponse).toList();
    }
}
