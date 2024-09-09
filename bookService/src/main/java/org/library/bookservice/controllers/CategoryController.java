package org.library.bookservice.controllers;

import lombok.AllArgsConstructor;
import org.library.bookservice.dto.category.CategoryRequest;
import org.library.bookservice.dto.category.CategoryResponse;
import org.library.bookservice.mapper.CategoryMapper;
import org.library.bookservice.mapper.Mapper;
import org.library.bookservice.model.Category;
import org.library.bookservice.service.AbstractService;
import org.library.bookservice.service.CategoryService;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@AllArgsConstructor
@RequestMapping("/api/categories")
public class CategoryController extends AbstractController<Category, CategoryRequest, CategoryResponse> {

    private final CategoryService service;
    private final CategoryMapper mapper;

    @Override
    protected AbstractService<Category> getService() {
        return service;
    }

    @Override
    protected Mapper<Category, CategoryResponse, CategoryRequest> getMapper() {
        return mapper;
    }
}
