package org.library.bookservice.datagen;

import lombok.AllArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.library.bookservice.model.*;
import org.library.bookservice.repository.*;
import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;

@AllArgsConstructor
@Service
@Slf4j
public class TestDataGenerator {

    private final AuthorRepository authorRepository;
    private final BookRepository bookRepository;
    private final CategoryRepository categoryRepository;
    private final GenreRepository genreRepository;
    private final PublisherRepository publisherRepository;

    @PostConstruct
    private void initializeDbWithTestData() {
        if (!bookRepository.findAll().isEmpty()) {
            log.info("Skipped data generation. Database already contains data.");
            return;
        }

        // Create Categories
        List<Category> categories = createCategories();
        categoryRepository.saveAll(categories);
        log.info("Saved categories: " + categories);

        // Create Genres
        List<Genre> genres = createGenres();
        genreRepository.saveAll(genres);
        log.info("Saved genres: " + genres);

        // Create Publishers
        List<Publisher> publishers = createPublishers();
        publisherRepository.saveAll(publishers);
        log.info("Saved publishers: " + publishers);

        // Create Authors and Books
        List<Author> authors = createAuthors();
        authorRepository.saveAll(authors);
        log.info("Saved authors: " + authors);

        createBooks(authors, categories, genres, publishers);
    }

    private List<Category> createCategories() {
        List<Category> categories = new ArrayList<>();

        Category fiction = new Category();
        fiction.setName("Fiction");
        fiction.setDescription("Fictional books");
        categories.add(fiction);

        Category nonFiction = new Category();
        nonFiction.setName("Non-Fiction");
        nonFiction.setDescription("Non-fictional books");
        categories.add(nonFiction);

        Category sciFi = new Category();
        sciFi.setName("Science Fiction");
        sciFi.setDescription("Sci-fi books");
        categories.add(sciFi);

        Category fantasy = new Category();
        fantasy.setName("Fantasy");
        fantasy.setDescription("Fantasy books");
        categories.add(fantasy);

        Category biography = new Category();
        biography.setName("Biography");
        biography.setDescription("Biographies");
        categories.add(biography);

        Category selfHelp = new Category();
        selfHelp.setName("Self-Help");
        selfHelp.setDescription("Self-help books");
        categories.add(selfHelp);

        return categories;
    }

    private List<Genre> createGenres() {
        List<Genre> genres = new ArrayList<>();

        Genre romance = new Genre();
        romance.setName("Romance");
        romance.setDescription("Romantic books");
        genres.add(romance);

        Genre thriller = new Genre();
        thriller.setName("Thriller");
        thriller.setDescription("Thrilling books");
        genres.add(thriller);

        Genre adventure = new Genre();
        adventure.setName("Adventure");
        adventure.setDescription("Adventure stories");
        genres.add(adventure);

        Genre mystery = new Genre();
        mystery.setName("Mystery");
        mystery.setDescription("Mystery novels");
        genres.add(mystery);

        Genre historical = new Genre();
        historical.setName("Historical");
        historical.setDescription("Historical literature");
        genres.add(historical);

        Genre horror = new Genre();
        horror.setName("Horror");
        horror.setDescription("Horror books");
        genres.add(horror);

        Genre fantasy = new Genre();
        fantasy.setName("Fantasy");
        fantasy.setDescription("Fantasy genre");
        genres.add(fantasy);

        return genres;
    }

    private List<Publisher> createPublishers() {
        List<Publisher> publishers = new ArrayList<>();

        Publisher penguin = new Publisher();
        penguin.setName("Penguin Books");
        penguin.setAddress("123 Penguin Street");
        publishers.add(penguin);

        Publisher harperCollins = new Publisher();
        harperCollins.setName("HarperCollins");
        harperCollins.setAddress("456 Harper Avenue");
        publishers.add(harperCollins);

        Publisher simonSchuster = new Publisher();
        simonSchuster.setName("Simon & Schuster");
        simonSchuster.setAddress("789 Simon Road");
        publishers.add(simonSchuster);

        Publisher macmillan = new Publisher();
        macmillan.setName("Macmillan");
        macmillan.setAddress("101 Macmillan Boulevard");
        publishers.add(macmillan);

        Publisher randomHouse = new Publisher();
        randomHouse.setName("Random House");
        randomHouse.setAddress("102 Random Lane");
        publishers.add(randomHouse);

        return publishers;
    }

    private List<Author> createAuthors() {
        List<Author> authors = new ArrayList<>();

        Author orwell = new Author();
        orwell.setName("George Orwell");
        orwell.setBio("Author of dystopian novels");
        authors.add(orwell);

        Author rowling = new Author();
        rowling.setName("J.K. Rowling");
        rowling.setBio("British author of the Harry Potter series");
        authors.add(rowling);

        Author king = new Author();
        king.setName("Stephen King");
        king.setBio("Author of horror novels");
        authors.add(king);

        Author austen = new Author();
        austen.setName("Jane Austen");
        austen.setBio("Known for novels about social issues");
        authors.add(austen);

        Author asimov = new Author();
        asimov.setName("Isaac Asimov");
        asimov.setBio("Author of science fiction and fantasy");
        authors.add(asimov);

        return authors;
    }

    private void createBooks(List<Author> authors, List<Category> categories, List<Genre> genres, List<Publisher> publishers) {
        List<Book> books = new ArrayList<>();

        Book book1 = new Book();
        book1.setTitle("1984");
        book1.setAuthor(authors.get(0));
        book1.setCategory(categories.get(0));
        book1.setDescription("A dystopian novel");
        book1.setISBN("9780451524935");
        book1.setPublisher(publishers.get(0));
        book1.setReleaseDate(LocalDate.of(1949, 6, 8));
        book1.setPrice(15.99);
        book1.setBookGenres(List.of(genres.get(0), genres.get(3)));
        books.add(book1);

        Book book2 = new Book();
        book2.setTitle("Harry Potter and the Philosopher's Stone");
        book2.setAuthor(authors.get(1));
        book2.setCategory(categories.get(3));
        book2.setDescription("A fantasy novel");
        book2.setISBN("9780747532743");
        book2.setPublisher(publishers.get(1));
        book2.setReleaseDate(LocalDate.of(1997, 6, 26));
        book2.setPrice(20.99);
        book2.setBookGenres(List.of(genres.get(6), genres.get(2)));
        books.add(book2);

        Book book3 = new Book();
        book3.setTitle("The Shining");
        book3.setAuthor(authors.get(2));
        book3.setCategory(categories.get(2));
        book3.setDescription("A horror novel");
        book3.setISBN("9780307743657");
        book3.setPublisher(publishers.get(2));
        book3.setReleaseDate(LocalDate.of(1977, 1, 28));
        book3.setPrice(18.50);
        book3.setBookGenres(List.of(genres.get(5)));
        books.add(book3);

        Book book4 = new Book();
        book4.setTitle("Pride and Prejudice");
        book4.setAuthor(authors.get(3));
        book4.setCategory(categories.get(0));
        book4.setDescription("A romantic novel");
        book4.setISBN("9780141439518");
        book4.setPublisher(publishers.get(3));
        book4.setReleaseDate(LocalDate.of(1813, 1, 28));
        book4.setPrice(12.99);
        book4.setBookGenres(List.of(genres.get(0), genres.get(4)));
        books.add(book4);

        Book book5 = new Book();
        book5.setTitle("Foundation");
        book5.setAuthor(authors.get(4));
        book5.setCategory(categories.get(1));
        book5.setDescription("A science fiction novel");
        book5.setISBN("9780553293357");
        book5.setPublisher(publishers.get(4));
        book5.setReleaseDate(LocalDate.of(1951, 6, 1));
        book5.setPrice(16.99);
        book5.setBookGenres(List.of(genres.get(2), genres.get(6)));
        books.add(book5);

        bookRepository.saveAll(books);
        log.info("Saved books: " + books);
    }
}
