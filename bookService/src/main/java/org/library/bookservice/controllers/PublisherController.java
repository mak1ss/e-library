package org.library.bookservice.controllers;

import lombok.AllArgsConstructor;
import org.library.bookservice.dto.publisher.PublisherRequest;
import org.library.bookservice.dto.publisher.PublisherResponse;
import org.library.bookservice.mapper.Mapper;
import org.library.bookservice.mapper.PublisherMapper;
import org.library.bookservice.model.Publisher;
import org.library.bookservice.service.AbstractService;
import org.library.bookservice.service.PublisherService;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@AllArgsConstructor
@RequestMapping("/api/publishers")
public class PublisherController extends AbstractController<Publisher, PublisherRequest, PublisherResponse> {

    private final PublisherService service;
    private final PublisherMapper mapper;

    @Override
    protected AbstractService<Publisher> getService() {
        return service;
    }

    @Override
    protected Mapper<Publisher, PublisherResponse, PublisherRequest> getMapper() {
        return mapper;
    }
}
