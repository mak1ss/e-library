package org.library.bookservice.mapper;

import lombok.AllArgsConstructor;
import lombok.RequiredArgsConstructor;
import org.library.bookservice.dto.book.BookRequest;
import org.library.bookservice.dto.book.BookResponse;
import org.library.bookservice.model.Book;
import org.library.bookservice.model.Genre;
import org.library.bookservice.service.AuthorService;
import org.library.bookservice.service.CategoryService;
import org.library.bookservice.service.GenreService;
import org.library.bookservice.service.PublisherService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Optional;

@Service
@RequiredArgsConstructor
public class BookMapper implements Mapper<Book, BookResponse, BookRequest> {

    private final AuthorService authorService;
    private final CategoryService categoryService;
    private final PublisherService publisherService;
    private final GenreService genreService;

    private final AuthorMapper authorMapper;
    private final CategoryMapper categoryMapper;
    private final PublisherMapper publisherMapper;
    private final GenreMapper genreMapper;

    @Value("${data.book.images.url-host}")
    private String imagesHost;

    @Value("${data.book.images.path}")
    private String imagesPath;

    @Override
    public Book requestToEntity(BookRequest request, Optional<Integer> id) {
        Book entity = new Book();

        entity.setId(id.orElse(null));
        entity.setTitle(request.getTitle());
        entity.setAuthor(authorService.getById(request.getAuthorId()).orElseThrow(
                () -> new IllegalArgumentException("Author not found")));
        entity.setCategory(categoryService.getById(request.getCategoryId()).orElseThrow(
                () -> new IllegalArgumentException("Category not found")));
        entity.setDescription(request.getDescription());
        entity.setISBN(request.getISBN());
        entity.setPublisher(publisherService.getById(request.getPublisherId()).orElseThrow(
                () -> new IllegalArgumentException("Publisher not found")));
        entity.setReleaseDate(request.getReleaseDate());
        entity.setPrice(request.getPrice());

        List<Genre> bookGenres = new ArrayList<>();
        request.getGenreIdList().stream().map(gId -> genreService.getById(gId).orElseThrow(
                () -> new IllegalArgumentException("Genre with id " + gId + " not found")
        )).forEach(bookGenres::add);

        entity.setGenres(bookGenres);

        return entity;
    }

    @Override
    public BookResponse entityToResponse(Book entity) {

        return BookResponse.builder()
                .id(entity.getId())
                .title(entity.getTitle())
                .author(authorMapper.entityToResponse(entity.getAuthor()))
                .category(categoryMapper.entityToResponse(entity.getCategory()))
                .description(entity.getDescription())
                .ISBN(entity.getISBN())
                .publisher(publisherMapper.entityToResponse(entity.getPublisher()))
                .releaseDate(entity.getReleaseDate())
                .price(entity.getPrice())
                .bookGenres(genreMapper.entitiesToListResponse(entity.getGenres()))
                .imageUrl(buildImageUrl(entity.getImageKey()))
                .averageRating(entity.getAverageRating())
                .totalReviews(entity.getTotalReviews())
                .build();

    }

    @Override
    public List<BookResponse> entitiesToListResponse(Collection<Book> entityList) {
        return entityList.stream().map(this::entityToResponse).toList();
    }

    private String buildImageUrl(String key) {
        return imagesHost + imagesPath + key;
    }
}
