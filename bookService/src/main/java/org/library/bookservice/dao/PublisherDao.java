package org.library.bookservice.dao;

import lombok.AllArgsConstructor;
import org.library.bookservice.model.Publisher;
import org.library.bookservice.repository.PrimaryRepository;
import org.library.bookservice.repository.PublisherRepository;
import org.springframework.stereotype.Service;

@AllArgsConstructor
@Service
public class PublisherDao extends AbstractDao<Publisher> {

    private PublisherRepository repo;

    @Override
    protected PrimaryRepository<Integer, Publisher> getRepository() {
        return repo;
    }
}
