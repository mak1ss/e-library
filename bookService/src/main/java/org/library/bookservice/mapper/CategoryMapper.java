package org.library.bookservice.mapper;

import org.library.bookservice.dto.category.CategoryRequest;
import org.library.bookservice.dto.category.CategoryResponse;
import org.library.bookservice.model.Category;
import org.springframework.stereotype.Service;

import java.util.Collection;
import java.util.List;
import java.util.Optional;

@Service
public class CategoryMapper implements Mapper<Category, CategoryResponse, CategoryRequest> {

    @Override
    public Category requestToEntity(CategoryRequest request, Optional<Integer> id) {
        Category entity = new Category();

        entity.setId(id.orElse(null));
        entity.setName(request.getName());

        return entity;
    }

    @Override
    public CategoryResponse entityToResponse(Category entity) {

        return CategoryResponse.builder()
                .id(entity.getId())
                .name(entity.getName())
                .build();
    }

    @Override
    public List<CategoryResponse> entitiesToListResponse(Collection<Category> entityList) {
        return entityList.stream().map(this::entityToResponse).toList();
    }
}
