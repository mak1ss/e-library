package org.library.reviewService.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.bson.types.ObjectId;
import org.library.reviewService.dto.AbstractRequest;
import org.library.reviewService.dto.AbstractResponse;
import org.library.reviewService.dto.PageResponse;
import org.library.reviewService.filter.FilterableProperty;
import org.library.reviewService.filter.FilteringOperation;
import org.library.reviewService.filter.SearchCriteria;
import org.library.reviewService.filter.model.DocumentFilterSpecificationBuilder;
import org.library.reviewService.mapper.IMapper;
import org.library.reviewService.model.base.Identifiable;
import org.library.reviewService.service.AbstractService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.convert.ConversionService;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.data.mongodb.core.query.Query;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Slf4j
public abstract class AbstractController<DocumentType extends Identifiable, RequestType extends AbstractRequest, ResponseType extends AbstractResponse> {

    private static final Pattern PATTERN = Pattern.compile("(\\w+?)(:|[!<>_]=?|=)(.*)");
    private static final String DEFAULT_PAGE_NUMBER = "0";
    private static final String DEFAULT_PAGE_SIZE = "5";

    @Autowired
    private ConversionService conversionService;

    protected abstract AbstractService<DocumentType> getService();

    protected abstract IMapper<DocumentType, RequestType, ResponseType> getMapper();

    protected DocumentFilterSpecificationBuilder getSpecificationBuilder() {return null;}

    @Operation(summary = "Get all", description = "Retrieve all entities")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "Successful operation"),
            @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    @GetMapping(produces = {MediaType.APPLICATION_JSON_VALUE})
    public ResponseEntity<PageResponse<ResponseType>> getAll(
            @RequestParam(required = false, defaultValue = DEFAULT_PAGE_NUMBER) Integer pageIndex,
            @RequestParam(required = false, defaultValue = DEFAULT_PAGE_SIZE) Integer pageSize,
            @RequestParam(required = false) Optional<String> search,
            @RequestParam(required = false) String[] sort
    ) {
        Sort parsedSort = convertSortingParams(sort);
        Query query = buildDefaultGetAllFiltering(search);
        Page<DocumentType> responseList = getService().getAll(query, PageRequest.of(pageIndex, pageSize, parsedSort));
        return ResponseEntity.ok(PageResponse.<ResponseType>builder()
                .size(responseList.getSize())
                .total(responseList.getTotalPages())
                .pageNumber(responseList.getNumber())
                .items(getMapper().entityToResponseList(responseList.getContent()))
                .build());
    }

    @Operation(summary = "Get", description = "Retrieve specific entity by ID")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "Successful operation"),
            @ApiResponse(responseCode = "404", description = "Not found"),
            @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    @GetMapping(path = "/{id}", produces = {MediaType.APPLICATION_JSON_VALUE})
    public ResponseEntity<Object> getRecord(@PathVariable String id) {
        if(!ObjectId.isValid(id)) {
            return ResponseEntity.badRequest().build();
        }

        Optional<DocumentType> entity = getService().getById(id);
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

        DocumentType entity = getMapper().requestToEntity(Optional.empty(), request);
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
    public ResponseEntity<ResponseType> updateRecord(@PathVariable String id, @Valid @RequestBody RequestType request) {
        if (request == null) {
            return ResponseEntity.badRequest().build();
        }

        DocumentType entity = getMapper().requestToEntity(Optional.of(id), request);
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
    public ResponseEntity<Object> deleteRecord(@PathVariable String id) {
        if (id == null) {
            return ResponseEntity.badRequest().build();
        }

        executeEntityDelete(id);
        return ResponseEntity.noContent().build();
    }

    protected Query buildDefaultGetAllFiltering(Optional<String> search) {
        if(search.isEmpty() || getSpecificationBuilder() == null) {
            return new Query();
        }
        List<FilterableProperty> filterableProperties = getSpecificationBuilder().getFilterableProperties();
        List<SearchCriteria> searchCriteria = parseSearchCriteria(search.get(), filterableProperties);
        return getSpecificationBuilder().buildSpecification(searchCriteria);
    }

    protected List<SearchCriteria> parseSearchCriteria(String search, List<FilterableProperty> filterableProperties) {
        String[] searchParams = search.split(",");
        List<SearchCriteria> searchCriteria = new ArrayList<>();
        for(String param : searchParams) {
            Matcher matcher = PATTERN.matcher(param);
            if(matcher.find()) {
                String key = matcher.group(1);
                String operator = matcher.group(2);
                String value = matcher.group(3);

                FilteringOperation operation = FilteringOperation.fromString(operator);
                Optional<FilterableProperty> property = filterableProperties.stream()
                        .filter(p -> p.getPropertyName().equals(key))
                        .findFirst();

                if(property.isPresent()) {
                    FilterableProperty filterableProperty = property.get();
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
        if(value.contains("||")) {
            return Arrays.stream(value.split("\\|\\|")).map(v -> conversionService.convert(v, expectedType)).toList();
        }
        return conversionService.convert(value, expectedType);
    }

    /**
     * @param sort
     * There is 2 options how sort is retrieving
     * 1. Single sort parameter - ["column1", "dir1"]
     * 2. Multiple sort params - ["column1,dir1","column2,dir2"]
     * they are converting into Sort.Order objects using substring based on index of ","
     **/
    private Sort convertSortingParams(String[] sort) {
        if(sort == null || sort.length == 0) {
            return Sort.unsorted();
        }
        if(!sort[0].contains(",")){
            return Sort.by(Sort.Direction.fromString(sort[1]), sort[0]);
        }

        List<Sort.Order> sortParams = Arrays.stream(sort)
                .map(s -> new Sort.Order(
                        Sort.Direction.fromString(s.substring(s.indexOf(",") + 1)),
                        s.substring(0, s.indexOf(","))))
                .toList();

        return Sort.by(sortParams);
    }

    protected DocumentType executeEntityCreate(DocumentType entity) {
        return getService().create(entity);
    }

    protected DocumentType executeEntityUpdate(DocumentType entity) {
        return getService().update(entity);
    }

    protected void executeEntityDelete(String id) {
        getService().deleteById(id);
    }
}
