CREATE TABLE book
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

CREATE TABLE author
(
    id        INT AUTO_INCREMENT PRIMARY KEY,
    name      VARCHAR(255) NOT NULL,
    biography TEXT,
    archived  BOOLEAN DEFAULT FALSE
);

CREATE TABLE genre
(
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description VARCHAR(255) NOT NULL,
    archived   BOOLEAN DEFAULT FALSE
);

CREATE TABLE category
(
    id            INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description VARCHAR(255) NOT NULL,
    archived      BOOLEAN DEFAULT FALSE
);

CREATE TABLE publisher
(
    id             INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    archived       BOOLEAN DEFAULT FALSE
);

CREATE TABLE book_genre
(
    id       INT AUTO_INCREMENT PRIMARY KEY,
    book_id  INT,
    genre_id INT
);

ALTER TABLE book
    ADD CONSTRAINT fk_books_author_id FOREIGN KEY (author_id) REFERENCES author (id),
    ADD CONSTRAINT fk_books_category_id FOREIGN KEY (category_id) REFERENCES category (id),
    ADD CONSTRAINT fk_books_publisher_id FOREIGN KEY (publisher_id) REFERENCES publisher (id);

ALTER TABLE book_genre
    ADD CONSTRAINT fk_book_genres_book_id FOREIGN KEY (book_id) REFERENCES book (id),
    ADD CONSTRAINT fk_book_genres_genre_id FOREIGN KEY (genre_id) REFERENCES genre (id),
    ADD CONSTRAINT uq_book_genre unique (book_id, genre_id);
