package org.library.bookservice.controllers;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.library.bookservice.dto.AbstractRequest;
import org.library.bookservice.dto.AbstractResponse;
import org.library.bookservice.filtering.FilterableProperty;
import org.library.bookservice.filtering.FilteringOperation;
import org.library.bookservice.filtering.SearchCriteria;
import org.library.bookservice.filtering.model.EntityFilterSpecificationBuilder;
import org.library.bookservice.mapper.Mapper;
import org.library.bookservice.model.base.Archivable;
import org.library.bookservice.model.base.Identifiable;
import org.library.bookservice.service.AbstractService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.convert.ConversionService;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Slf4j
public abstract class AbstractController<T extends Identifiable & Archivable, RequestType extends AbstractRequest, ResponseType extends AbstractResponse> {

    private static final Pattern PATTERN = Pattern.compile("(\\w+?)(:|[!<>]=?|=)(.*)");

    @Autowired
    private ConversionService conversionService;

    protected abstract AbstractService<T> getService();

    protected abstract Mapper<T, ResponseType, RequestType> getMapper();

    protected EntityFilterSpecificationBuilder<T> getSpecificationBuilder() {
        return null;
    }

    @Operation(summary = "Get all", description = "Retrieve all entities")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "Successful operation"),
            @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    @GetMapping(produces = {MediaType.APPLICATION_JSON_VALUE})
    public ResponseEntity<List<ResponseType>> getAll(
            @RequestParam Integer pageIndex,
            @RequestParam Integer pageSize,
            @RequestParam(required = false) Optional<String> search
    ) {

        Specification<T> filter = buildDefaultGetAllFiltering(search);

        List<ResponseType> responseList = getMapper().entitiesToListResponse(getService().getAll(PageRequest.of(pageIndex, pageSize), filter));
        return ResponseEntity.ok(responseList);
    }

    @Operation(summary = "Get", description = "Retrieve specific entity by ID")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "Successful operation"),
            @ApiResponse(responseCode = "404", description = "Not found"),
            @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    @GetMapping(path = "/{id}", produces = {MediaType.APPLICATION_JSON_VALUE})
    public ResponseEntity<Object> getRecord(@PathVariable Integer id) {
        Optional<T> entity = getService().getById(id);
        return entity.<ResponseEntity<Object>>map(e -> ResponseEntity.ok(getMapper().entityToResponse(e)))
                .orElse(ResponseEntity.notFound().build());
    }

    @Operation(summary = "Create", description = "Create new entity")
    @ApiResponses({
            @ApiResponse(responseCode = "201", description = "Created successfully"),
            @ApiResponse(responseCode = "400", description = "Bad request"),
            @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    @PostMapping(
            consumes = MediaType.APPLICATION_JSON_VALUE,
            produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<ResponseType> createRecord(@Valid @RequestBody RequestType request) {
        if (request == null) {
            return ResponseEntity.badRequest().build();
        }

        T entity = getMapper().requestToEntity(request, Optional.empty());
        entity = executeEntityCreate(entity);
        ResponseType response = getMapper().entityToResponse(entity);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @Operation(summary = "Update", description = "Update entity")
    @ApiResponses({
            @ApiResponse(responseCode = "201", description = "Updated successfully"),
            @ApiResponse(responseCode = "400", description = "Bad request"),
            @ApiResponse(responseCode = "404", description = "Not found"),
            @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    @PutMapping(path = "/{id}",
            consumes = MediaType.APPLICATION_JSON_VALUE,
            produces = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<ResponseType> updateRecord(@PathVariable Integer id, @Valid @RequestBody RequestType request) {
        if (request == null) {
            return ResponseEntity.badRequest().build();
        }

        T entity = getMapper().requestToEntity(request, id.describeConstable());
        entity = executeEntityUpdate(entity);
        ResponseType response = getMapper().entityToResponse(entity);
        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @Operation(summary = "Delete", description = "Delete entity")
    @ApiResponses({
            @ApiResponse(responseCode = "204", description = "Deleted successfully"),
            @ApiResponse(responseCode = "404", description = "Not found"),
            @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    @DeleteMapping(path = "/{id}")
    public ResponseEntity<Object> deleteRecord(@PathVariable Integer id) {
        if (id == null) {
            return ResponseEntity.badRequest().build();
        }

        executeEntityDelete(id);
        return ResponseEntity.noContent().build();
    }

    protected Specification<T> buildDefaultGetAllFiltering(Optional<String> search) {
        if(search.isEmpty() || getSpecificationBuilder() == null) {
            return null;
        }
        List<FilterableProperty<T>> filterableProperties = getSpecificationBuilder().getFilterableProperties();
        List<SearchCriteria> searchCriteria = parseSearchCriteria(search.get(), filterableProperties);
        return getSpecificationBuilder().buildSpecification(searchCriteria);
    }

    protected List<SearchCriteria> parseSearchCriteria(String search, List<FilterableProperty<T>> filterableProperties) {
        String[] searchParams = search.split(",");
        List<SearchCriteria> searchCriteria = new ArrayList<>();
        for(String param : searchParams) {
            Matcher matcher = PATTERN.matcher(param);
            if(matcher.find()) {
                String key = matcher.group(1);
                String operator = matcher.group(2);
                String value = matcher.group(3);

                FilteringOperation operation = FilteringOperation.fromString(operator);
                Optional<FilterableProperty<T>> property = filterableProperties.stream()
                        .filter(p -> p.getPropertyName().equals(key))
                        .findFirst();

                if(property.isPresent()) {
                    FilterableProperty<T> filterableProperty = property.get();
                    if(!filterableProperty.getSupportedOperations().contains(operation)) {
                        throw new UnsupportedOperationException("Unsupported filtering operation '" + operator + "' for property '" + key + "'");
                    }
                    Object convertedValue;
                    if(value.isEmpty()) {
                        convertedValue = null;
                    } else {
                        convertedValue = convertFilteringValue(value, filterableProperty.getExpectedType());
                    }
                    searchCriteria.add(new SearchCriteria(key, operation, convertedValue));

                } else {
                    log.warn("[{}] is unsupported property, filtering skipped", key);
                }
            } else {
                log.warn("Unrecognisable searching input: {}", search);
            }
        }
        return searchCriteria;
    }

    protected Object convertFilteringValue(String value, Class<?> expectedType) {
        return conversionService.convert(value, expectedType);
    }

    protected T executeEntityCreate(T entity) {
        return getService().save(entity);
    }

    protected T executeEntityUpdate(T entity) {
        return getService().update(entity);
    }

    protected void executeEntityDelete(Integer id) {
        getService().deleteById(id);
    }
}
