package org.library.bookservice.dao;

import lombok.AllArgsConstructor;
import org.library.bookservice.model.Category;
import org.library.bookservice.repository.CategoryRepository;
import org.library.bookservice.repository.PrimaryRepository;
import org.springframework.stereotype.Service;

@AllArgsConstructor
@Service
public class CategoryDao extends AbstractDao<Category> {

    private CategoryRepository repo;

    @Override
    protected PrimaryRepository<Integer, Category> getRepository() {
        return repo;
    }
}
