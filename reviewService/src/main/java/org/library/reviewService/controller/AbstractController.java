package org.library.reviewService.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import jakarta.validation.Valid;
import org.bson.types.ObjectId;
import org.library.reviewService.dto.AbstractRequest;
import org.library.reviewService.dto.AbstractResponse;
import org.library.reviewService.mapper.IMapper;
import org.library.reviewService.model.base.Identifiable;
import org.library.reviewService.service.AbstractService;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;


public abstract class AbstractController<DocumentType extends Identifiable, RequestType extends AbstractRequest, ResponseType extends AbstractResponse> {

    protected abstract AbstractService<DocumentType> getService();

    protected abstract IMapper<DocumentType, RequestType, ResponseType> getMapper();

    @Operation(summary = "Get all", description = "Retrieve all entities")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "Successful operation"),
            @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    @GetMapping(produces = {MediaType.APPLICATION_JSON_VALUE})
    public ResponseEntity<List<ResponseType>> getAll(
            @RequestParam Integer pageIndex,
            @RequestParam Integer pageSize
    ) {

        List<ResponseType> responseList = getMapper().entityToResponseList(getService().getAll(PageRequest.of(pageIndex, pageSize)));
        return ResponseEntity.ok(responseList);
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
