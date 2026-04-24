package org.library.reviewService.util;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.library.reviewService.client.response.BookResponse;
import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Utility to aggregate book metadata for semantic relevance scoring.
 * Follows Strategy C from design: selective fields aggregation.
 * Produces 100-250 tokens for optimal embedding generation.
 * 
 * Fields included:
 * - Title (always)
 * - Author name (if available)
 * - Category name (if available)
 * - Genres (if available)
 * - Description (if available, highest semantic value)
 * - ISBN (for disambiguity)
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class BookMetadataAggregator {

    private final ObjectMapper objectMapper;

    /**
     * Aggregates book metadata fields into a JSON string for semantic embedding.
     * Extracts from nested BookResponse objects (author, category, genres).
     * 
     * Includes: title, author name, category name, genres, description to provide sufficient context
     * for scoring review relevance to the book's content and themes.
     *
     * Follows Strategy C: selective fields with logical ordering for better token efficiency.
     *
     * @param book The BookResponse object from book service (with nested objects)
     * @return JSON string containing aggregated metadata, or empty JSON on error
     */
    public String aggregateMetadata(BookResponse book) {
        try {
            if (book == null) {
                log.warn("BookResponse is null, returning empty metadata");
                return "{}";
            }

            Map<String, Object> metadata = new HashMap<>();
            
            // Always include title (required field)
            if (book.getTitle() != null && !book.getTitle().isBlank()) {
                metadata.put("title", book.getTitle().trim());
            }
            
            // Extract and include author name from nested author object
            if (book.getAuthor() != null && book.getAuthor().getName() != null 
                    && !book.getAuthor().getName().isBlank()) {
                metadata.put("author_name", book.getAuthor().getName().trim());
            }
            
            // Extract and include category name from nested category object
            if (book.getCategory() != null && book.getCategory().getName() != null
                    && !book.getCategory().getName().isBlank()) {
                metadata.put("category_name", book.getCategory().getName().trim());
            }
            
            // Extract and include genres as comma-separated string from list
            if (book.getBookGenres() != null && !book.getBookGenres().isEmpty()) {
                String genresStr = book.getBookGenres().stream()
                        .filter(g -> g != null && g.getName() != null)
                        .map(BookResponse.GenreResponse::getName)
                        .filter(name -> !name.isBlank())
                        .collect(Collectors.joining(", "));
                
                if (!genresStr.isBlank()) {
                    metadata.put("genres", genresStr);
                }
            }
            
            // Include description last (highest priority for semantic content)
            // Description is the most information-rich field for relevance scoring
            if (book.getDescription() != null && !book.getDescription().isBlank()) {
                metadata.put("description", book.getDescription().trim());
            }
            
            // Include ISBN for disambiguity
            if (book.getISBN() != null && !book.getISBN().isBlank()) {
                metadata.put("isbn", book.getISBN().trim());
            }

            String result = objectMapper.writeValueAsString(metadata);
            
            log.debug("Aggregated book metadata for book id {}: {} fields, {} bytes",
                    book.getId(), metadata.size(), result.length());
            
            return result;
        } catch (Exception e) {
            log.error("Error aggregating book metadata for book id {}: {}",
                    book != null ? book.getId() : "unknown", e.getMessage());
            return "{}";
        }
    }
}
