package org.library.reviewService.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import lombok.AllArgsConstructor;
import org.library.reviewService.dto.reviewMetrics.ReviewMetricsResponse;
import org.library.reviewService.model.ReviewMetrics;
import org.library.reviewService.service.ReviewMetricsService;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@AllArgsConstructor
@RequestMapping("/api/review-metrics")
public class ReviewMetricsController {

    private final ReviewMetricsService service;

    @Operation(summary = "Get all", description = "Retrieve all entities")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "Successful operation"),
            @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    @GetMapping(produces = {MediaType.APPLICATION_JSON_VALUE})
    public ResponseEntity<List<ReviewMetricsResponse>> getAll(
            @RequestParam Integer pageIndex,
            @RequestParam Integer pageSize
    ) {

        List<ReviewMetricsResponse> responseList = service.getAll(PageRequest.of(pageIndex, pageSize)).stream()
                .map(ReviewMetricsService::mapToResponse)
                .toList();
        return ResponseEntity.ok(responseList);
    }

    @Operation(summary = "Get", description = "Retrieve specific entity by ID")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "Successful operation"),
            @ApiResponse(responseCode = "404", description = "Not found"),
            @ApiResponse(responseCode = "500", description = "Internal server error")
    })
    @GetMapping(path = "/by-book/{bookId}", produces = {MediaType.APPLICATION_JSON_VALUE})
    public ResponseEntity<Object> getRecord(@PathVariable Integer bookId) {
      Optional<ReviewMetrics> entity = service.getByBookId(bookId);
        return entity.<ResponseEntity<Object>>map(e -> ResponseEntity.ok(ReviewMetricsService.mapToResponse(e)))
                .orElse(ResponseEntity.notFound().build());
    }
}
