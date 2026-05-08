package org.library.bookservice.controllers;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.security.SecurityRequirement;
import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.library.bookservice.client.RecommenderServiceClient;
import org.library.bookservice.client.ReviewServiceClient;
import org.library.bookservice.dto.PageResponse;
import org.library.bookservice.dto.book.BookRequest;
import org.library.bookservice.dto.book.BookResponse;
import org.library.bookservice.dto.recommender.ExplanationDetails;
import org.library.bookservice.dto.recommender.GetPersonalizedRecommendationsRequest;
import org.library.bookservice.dto.recommender.GetSimilarBooksRequest;
import org.library.bookservice.dto.recommender.PersonalizedRecommendationResponse;
import org.library.bookservice.dto.recommender.SimilarBookResponse;
import org.library.bookservice.dto.review.ReviewResponse;
import org.library.bookservice.filtering.model.EntityFilterSpecificationBuilder;
import org.library.bookservice.filtering.model.book.BookSpecificationBuilder;
import org.library.bookservice.mapper.BookMapper;
import org.library.bookservice.mapper.Mapper;
import org.library.bookservice.model.Book;
import org.library.bookservice.service.AbstractService;
import org.library.bookservice.service.BookService;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.*;
import java.util.stream.Collectors;

@Slf4j
@RestController
@AllArgsConstructor
@RequestMapping("/api/books")
@SecurityRequirement(name = "standardFlow")
@SecurityRequirement(name = "clientCredentialsFlow")
public class BookController extends AbstractController<Book, BookRequest, BookResponse> {

    private final BookService service;
    private final BookMapper mapper;
    private final BookSpecificationBuilder specificationBuilder;
    private final RecommenderServiceClient recommenderServiceClient;
    private final ReviewServiceClient reviewServiceClient;

    @Override
    protected AbstractService<Book> getService() {
        return service;
    }

    @Override
    protected Mapper<Book, BookResponse, BookRequest> getMapper() {
        return mapper;
    }

    @Override
    protected EntityFilterSpecificationBuilder<Book> getSpecificationBuilder() {
        return specificationBuilder;
    }

    @Override
    protected void executeEntityDelete(Integer id) {
        getService().getById(id).ifPresentOrElse(book -> {
            if (book.isArchived()) {
                log.info("Archived book was tried to delete. ID: {}", book.getId());
                return;
            }
            getService().delete(book);
        }, () -> {
            throw new NoSuchElementException();
        });
    }

    @PostMapping("/{id}/cover")
    public ResponseEntity<BookResponse> uploadCover(
            @PathVariable Integer id,
            @RequestParam("file") MultipartFile file) {
        Book book = service.uploadCoverImage(id, file);
        return ResponseEntity.ok(mapper.entityToResponse(book));
    }

    /**
     * Get similar books for a given book using content-based filtering
     * Real-time computation (no caching)
     */
    @GetMapping("/{bookId}/similar")
    @Operation(summary = "Get similar books", description = "Get similar books using content-based filtering (TF-IDF)")
    public ResponseEntity<PageResponse<BookResponse>> getSimilarBooks(
            @PathVariable Integer bookId,
            @RequestParam(defaultValue = "10") Integer topK,
            Pageable pageable) {

        try {
            // Validate book exists
            Optional<Book> seedBook = service.getById(bookId);
            if (seedBook.isEmpty()) {
                throw new NoSuchElementException("Book not found: " + bookId);
            }

            // Call recommenderService (content-based, real-time)
            GetSimilarBooksRequest request = GetSimilarBooksRequest.builder()
                    .bookId(bookId)
                    .topK(Math.min(topK, 50))  // Max 50
                    .build();

            ResponseEntity<List<SimilarBookResponse>> similarResponse =
                    recommenderServiceClient.getSimilarBooks(request);

            if (similarResponse.getStatusCode() != HttpStatus.OK || similarResponse.getBody() == null) {
                return ResponseEntity.ok(PageResponse.<BookResponse>builder()
                        .size(0)
                        .total(0L)
                        .pageNumber(0)
                        .items(Collections.emptyList())
                        .build());
            }

            // Fetch full book details for each similar book
            List<SimilarBookResponse> similarRecs = similarResponse.getBody();
            List<BookResponse> similarBooks = new ArrayList<>();
            
            // Create map to store explanations
            Map<Integer, ExplanationDetails> explanations = new HashMap<>();

            for (SimilarBookResponse rec : similarRecs) {
                try {
                    Optional<Book> book = service.getById(rec.getBookId());
                    if (book.isPresent() && !book.get().isArchived()) {
                        BookResponse bookResponse = getMapper().entityToResponse(book.get());
                        // Preserve explanation from recommenderService
                        if (rec.getExplanation() != null) {
                            bookResponse.setExplanation(rec.getExplanation());
                            explanations.put(rec.getBookId(), rec.getExplanation());
                        }
                        similarBooks.add(bookResponse);
                    }
                } catch (Exception e) {
                    log.warn("Failed to fetch similar book details: {}", rec.getBookId());
                }
            }

            // Return paginated response
            PageResponse<BookResponse> result = PageResponse.<BookResponse>builder()
                    .size(pageable.getPageSize())
                    .total((long) similarBooks.size())
                    .pageNumber(pageable.getPageNumber())
                    .items(similarBooks)
                    .build();

            return ResponseEntity.ok(result);

        } catch (NoSuchElementException e) {
            log.error("Seed book not found: {}", bookId);
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            log.error("Error fetching similar books", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Get personalized recommendations for authenticated user
     * Uses item-item collaborative filtering (real-time, no caching)
     * Falls back to popular books if user has no history
     */
    @GetMapping("/recommendations/personal")
    @PreAuthorize("isAuthenticated()")
    @Operation(summary = "Get personalized recommendations", description = "Get recommendations for authenticated user based on review history")
    public ResponseEntity<PageResponse<BookResponse>> getPersonalizedRecommendations(
            @RequestParam(defaultValue = "10") Integer topK,
            @AuthenticationPrincipal Jwt jwt,
            Pageable pageable) {

        try {
            // Extract user ID from JWT
            String userId = jwt.getClaimAsString("sub");
            if (userId == null) {
                throw new SecurityException("User ID not found in token");
            }

            // Fetch user's complete review history (all reviews, no pagination limit)
            ResponseEntity<PageResponse<ReviewResponse>> reviewResponse =
                    reviewServiceClient.getUserReviewedBooks(userId);

            List<GetPersonalizedRecommendationsRequest.SeedBook> seedBooks = new ArrayList<>();
            if (reviewResponse.getStatusCode() == HttpStatus.OK && reviewResponse.getBody() != null) {
                // Deduplicate by bookId, keeping the highest rating in case of re-reviews
                Map<Integer, Integer> seedBookRatings = reviewResponse.getBody().getItems().stream()
                        .collect(Collectors.toMap(
                                ReviewResponse::getBookId,
                                ReviewResponse::getRating,
                                Integer::max
                        ));
                seedBooks = seedBookRatings.entrySet().stream()
                        .map(e -> new GetPersonalizedRecommendationsRequest.SeedBook(e.getKey(), e.getValue()))
                        .collect(Collectors.toList());
            }

            List<BookResponse> recommendations = new ArrayList<>();

            // Case 1: User has review history → use collaborative filtering (real-time)
            if (!seedBooks.isEmpty()) {
                recommendations = computePersonalizedRecommendations(seedBooks, topK);
            }

            // Case 2: No history → use popular books
            if (recommendations.isEmpty()) {
                recommendations = getPopularBooks(topK);
            }

            PageResponse<BookResponse> result = PageResponse.<BookResponse>builder()
                    .size(pageable.getPageSize())
                    .total((long) recommendations.size())
                    .pageNumber(pageable.getPageNumber())
                    .items(recommendations)
                    .build();

            return ResponseEntity.ok(result);

        } catch (SecurityException e) {
            log.error("Unauthorized: {}", e.getMessage());
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        } catch (Exception e) {
            log.error("Error fetching personalized recommendations", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }

    /**
     * Helper: Compute recommendations via recommenderService (real-time, no caching)
     */
    private List<BookResponse> computePersonalizedRecommendations(
            List<GetPersonalizedRecommendationsRequest.SeedBook> seedBooks, Integer topK) {
        try {
            // Call recommenderService (collaborative filtering)
            GetPersonalizedRecommendationsRequest request = GetPersonalizedRecommendationsRequest.builder()
                    .userSeedBooks(seedBooks)
                    .topK(Math.min(topK, 50))  // Max 50
                    .build();

            ResponseEntity<List<PersonalizedRecommendationResponse>> response =
                    recommenderServiceClient.getPersonalizedRecommendations(request);

            if (response.getStatusCode() != HttpStatus.OK || response.getBody() == null) {
                return Collections.emptyList();
            }

            List<PersonalizedRecommendationResponse> recommendations = response.getBody();

            // Build map of seed books for explanation enrichment
            Map<Integer, BookResponse> seedBooksMap = new HashMap<>();
            for (GetPersonalizedRecommendationsRequest.SeedBook seed : seedBooks) {
                Optional<Book> seedBook = service.getById(seed.getBookId());
                if (seedBook.isPresent()) {
                    seedBooksMap.put(seed.getBookId(), getMapper().entityToResponse(seedBook.get()));
                }
            }

            List<BookResponse> result = new ArrayList<>();
            for (PersonalizedRecommendationResponse rec : recommendations) {
                try {
                    Optional<Book> book = service.getById(rec.getBookId());
                    if (book.isPresent() && !book.get().isArchived()) {
                        BookResponse bookResponse = getMapper().entityToResponse(book.get());
                        
                        // Preserve and enrich explanation from recommenderService
                        if (rec.getExplanation() != null) {
                            enrichExplanationWithBookTitles(bookResponse, rec.getExplanation(), seedBooksMap);
                        }
                        
                        result.add(bookResponse);
                    }
                } catch (Exception e) {
                    log.warn("Failed to fetch book: {}", rec.getBookId());
                }
            }

            return result;

        } catch (Exception e) {
            log.error("Error computing personalized recommendations", e);
            return Collections.emptyList();
        }
    }

    /**
     * Helper: Get popular books (for new/unauthenticated users)
     */
    private List<BookResponse> getPopularBooks(Integer topK) {
        try {
            // Get popular books: sorted by average rating and number of reviews
            Pageable pageable = PageRequest.of(0, topK, Sort.by("averageRating").descending()
                    .and(Sort.by("totalReviews").descending()));
            
            return service.getAll(pageable, null).getContent().stream()
                    .map(getMapper()::entityToResponse)
                    .collect(Collectors.toList());
        } catch (Exception e) {
            log.error("Error fetching popular books", e);
            return Collections.emptyList();
        }
    }

    /**
     * Helper: Enrich personalized recommendation explanation with book titles
     */
    private void enrichExplanationWithBookTitles(
            BookResponse bookResponse,
            ExplanationDetails explanation,
            Map<Integer, BookResponse> seedBooksMap) {
        
        if (explanation == null || explanation.getTopContributors() == null || explanation.getTopContributors().isEmpty()) {
            return;
        }
        
        // Try to get the first contributor (seed book ID) and replace with title
        String firstContributor = explanation.getTopContributors().get(0);
        
        try {
            Integer seedBookId = Integer.parseInt(firstContributor);
            BookResponse seedBook = seedBooksMap.get(seedBookId);
            
            if (seedBook != null) {
                // Update primary reason with actual book title
                String updatedReason = "Based on your review of '" + seedBook.getTitle() + "'";
                explanation.setPrimaryReason(updatedReason);
                
                // Replace contributor ID with book title
                explanation.setTopContributors(Collections.singletonList(seedBook.getTitle()));
                
                // Set explanation on book response
                bookResponse.setExplanation(explanation);
            }
        } catch (NumberFormatException e) {
            // Not a numeric ID, keep as-is
            bookResponse.setExplanation(explanation);
        }
    }
}
