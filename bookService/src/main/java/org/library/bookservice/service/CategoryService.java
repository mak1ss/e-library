package org.library.bookservice.service;

import lombok.AllArgsConstructor;
import org.library.bookservice.dao.AbstractDao;
import org.library.bookservice.dao.CategoryDao;
import org.library.bookservice.model.Category;
import org.springframework.stereotype.Service;

@AllArgsConstructor
@Service
public class CategoryService extends AbstractService<Category> {

    private CategoryDao dao;

    @Override
    protected AbstractDao<Category> getDao() {
        return dao;
    }
}
