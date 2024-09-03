CREATE TABLE books
(
    id           INT AUTO_INCREMENT PRIMARY KEY,
    title        VARCHAR(255) NOT NULL,
    author_id    INT          NOT NULL,
    category_id  INT          NOT NULL,
    description  TEXT,
    isbn         VARCHAR(20),
    publisher_id INT,
    release_date DATE,
    price        DECIMAL(10, 2),
    archived     BOOLEAN DEFAULT FALSE
);

CREATE TABLE authors
(
    id        INT AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(255) NOT NULL,
    biography TEXT,
    archived  BOOLEAN DEFAULT FALSE
);

CREATE TABLE genres
(
    id         INT AUTO_INCREMENT PRIMARY KEY,
    genre_name VARCHAR(255) NOT NULL,
    archived   BOOLEAN DEFAULT FALSE
);

CREATE TABLE categories
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL,
    archived      BOOLEAN DEFAULT FALSE
);

CREATE TABLE publishers
(
    id             INT AUTO_INCREMENT PRIMARY KEY,
    publisher_name VARCHAR(255) NOT NULL,
    archived       BOOLEAN DEFAULT FALSE
);

CREATE TABLE book_reviews
(
    id           INT AUTO_INCREMENT PRIMARY KEY,
    book_id      INT,
    user_id      INT,
    review_text  TEXT,
    rating_value INT CHECK (rating_value >= 1 AND rating_value <= 5),
    review_date  DATETIME NOT NULL,
    archived     BOOLEAN DEFAULT FALSE
);

CREATE TABLE book_ratings
(
    id             INT AUTO_INCREMENT PRIMARY KEY,
    book_id        INT,
    average_rating DECIMAL(3, 2),
    ratings_count  INT,
    archived       BOOLEAN DEFAULT FALSE
);

CREATE TABLE book_genres
(
    id       INT AUTO_INCREMENT PRIMARY KEY,
    book_id  INT,
    genre_id INT,
    archived BOOLEAN DEFAULT FALSE,
    PRIMARY KEY (book_id, genre_id)
);

ALTER TABLE books
    ADD CONSTRAINT fk_books_author_id FOREIGN KEY (author_id) REFERENCES authors (id),
    ADD CONSTRAINT fk_books_category_id FOREIGN KEY (category_id) REFERENCES categories (id),
    ADD CONSTRAINT fk_books_publisher_id FOREIGN KEY (publisher_id) REFERENCES publishers (id);

ALTER TABLE book_reviews
    ADD CONSTRAINT fk_book_reviews_book_id FOREIGN KEY (book_id) REFERENCES books (id);

ALTER TABLE book_ratings
    ADD CONSTRAINT fk_book_ratings_book_id FOREIGN KEY (book_id) REFERENCES books (id);

ALTER TABLE book_genres
    ADD CONSTRAINT fk_book_genres_book_id FOREIGN KEY (book_id) REFERENCES books (id),
    ADD CONSTRAINT fk_book_genres_genre_id FOREIGN KEY (genre_id) REFERENCES genres (id);
