package org.library.bookservice.service;

import lombok.AllArgsConstructor;
import org.library.bookservice.dao.AbstractDao;
import org.library.bookservice.dao.PublisherDao;
import org.library.bookservice.model.Publisher;
import org.springframework.stereotype.Service;

@AllArgsConstructor
@Service
public class PublisherService extends AbstractService<Publisher> {

    private PublisherDao dao;

    @Override
    protected AbstractDao<Publisher> getDao() {
        return dao;
    }
}
