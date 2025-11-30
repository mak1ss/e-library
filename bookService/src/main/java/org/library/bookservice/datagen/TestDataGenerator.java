package org.library.bookservice.datagen;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.library.bookservice.model.*;
import org.library.bookservice.repository.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import jakarta.annotation.PostConstruct;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.function.Function;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class TestDataGenerator {

    private final AuthorRepository authorRepository;
    private final BookRepository bookRepository;
    private final CategoryRepository categoryRepository;
    private final GenreRepository genreRepository;
    private final PublisherRepository publisherRepository;
    private final ObjectMapper objectMapper;

    @Value("${data.seeding.folder}")
    private String seedingFolder;

    @Value("${data.seeding.categories}")
    private String categoriesFile;

    @Value("${data.seeding.genres}")
    private String genresFile;

    @Value("${data.seeding.publishers}")
    private String publishersFile;

    @Value("${data.seeding.authors}")
    private String authorsFile;

    @Value("${data.seeding.books}")
    private String booksFile;

    @PostConstruct
    public void initializeDbWithTestData() {
        if (bookRepository.count() > 0) {
            log.info("Database already initialized. Skipping data seeding.");
            return;
        }

        try {
            List<Category> categories = loadData(categoriesFile, new TypeReference<>() {
            });
            categories = categoryRepository.saveAll(categories);
            log.info("Loaded {} categories", categories.size());

            List<Genre> genres = loadData(genresFile, new TypeReference<>() {
            });
            genres = genreRepository.saveAll(genres);
            log.info("Loaded {} genres", genres.size());

            List<Publisher> publishers = loadData(publishersFile, new TypeReference<>() {
            });
            publishers = publisherRepository.saveAll(publishers);
            log.info("Loaded {} publishers", publishers.size());

            List<Author> authors = loadData(authorsFile, new TypeReference<>() {
            });
            authors = authorRepository.saveAll(authors);
            log.info("Loaded {} authors", authors.size());

            Map<String, Category> categoryMap = categories.stream()
                .collect(Collectors.toMap(Category::getName, Function.identity()));
            Map<String, Genre> genreMap = genres.stream()
                .collect(Collectors.toMap(Genre::getName, Function.identity()));
            Map<String, Publisher> publisherMap = publishers.stream()
                .collect(Collectors.toMap(Publisher::getName, Function.identity()));
            Map<String, Author> authorMap = authors.stream()
                .collect(Collectors.toMap(Author::getName, Function.identity()));

            List<BookSeedDto> bookDtos = loadData(booksFile, new TypeReference<>() {
            });
            List<Book> books = new ArrayList<>();

            for (BookSeedDto dto : bookDtos) {
                Book book = new Book();
                book.setTitle(dto.getTitle());
                book.setISBN(dto.getIsbn());
                book.setDescription(dto.getDescription());
                book.setReleaseDate(dto.getReleaseDate());
                book.setPrice(dto.getPrice());
                book.setImageKey(dto.getImageKey());

                if (categoryMap.containsKey(dto.getCategory())) {
                    book.setCategory(categoryMap.get(dto.getCategory()));
                } else {
                    log.warn("Category not found: {}", dto.getCategory());
                }

                if (publisherMap.containsKey(dto.getPublisher())) {
                    book.setPublisher(publisherMap.get(dto.getPublisher()));
                } else {
                    log.warn("Publisher not found: {}", dto.getPublisher());
                }

                if (authorMap.containsKey(dto.getAuthor())) {
                    book.setAuthor(authorMap.get(dto.getAuthor()));
                } else {
                    log.warn("Author not found: {}", dto.getAuthor());
                }

                if (dto.getGenres() != null) {
                    List<Genre> bookGenres = dto.getGenres().stream()
                        .filter(genreMap::containsKey)
                        .map(genreMap::get)
                        .toList();
                    book.setGenres(bookGenres);
                }

                books.add(book);
            }

            bookRepository.saveAll(books);
            log.info("Successfully loaded {} books into database", books.size());

        } catch (IOException e) {
            log.error("Failed to seed data: {}", e.getMessage(), e);
            throw new RuntimeException("Data seeding failed", e);
        }
    }

    /**
     * Helper method to read JSON files.
     * Автоматично об'єднує seedingFolder та fileName.
     */
    private <T> List<T> loadData(String fileName, TypeReference<List<T>> typeReference) throws IOException {
        String fullPath = Paths.get(seedingFolder, fileName).toString();

        log.debug("Reading data from file: {}", fullPath);

        try (InputStream inputStream = new FileInputStream(fullPath)) {
            return objectMapper.readValue(inputStream, typeReference);
        }
    }
}