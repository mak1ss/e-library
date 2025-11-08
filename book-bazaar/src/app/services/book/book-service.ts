import { inject, Injectable } from '@angular/core';
import { Book } from '../../model/book';
import { HttpClient } from '@angular/common/http';
import { Publisher } from '../../model/publisher';
import { Genre } from '../../model/genre';
import { Author } from '../../model/author';
import { Category } from '../../model/category';

@Injectable({
  providedIn: 'root',
})
export class BookService {

  private http: HttpClient = inject(HttpClient);

  browsingGenres: Genre[] = [
    new Genre(1, "Comedy"),
    new Genre(1, "Romance"),
    new Genre(1, "Adventure"),
    new Genre(1, "Business")
  ];

  popularBooks: Book[] = [
    new Book(1, "1983", new Author(1, "Orwell"), new Category(1, "Fiction"), "Anti-utopy", "21938432", new Publisher(1, "World Books"), "1953-10-05", 30.22, this.browsingGenres, "book-image.png"),
    new Book(2, "1983", new Author(1, "Orwell"), new Category(1, "Fiction"), "Anti-utopy", "21938432", new Publisher(1, "World Books"), "1953-10-05", 30.22, this.browsingGenres, "book-image.png"),
    new Book(3, "1983", new Author(1, "Orwell"), new Category(1, "Fiction"), "Anti-utopy", "21938432", new Publisher(1, "World Books"), "1953-10-05", 30.22, this.browsingGenres, "book-image.png"),
    new Book(4, "1983", new Author(1, "Orwell"), new Category(1, "Fiction"), "Anti-utopy", "21938432", new Publisher(1, "World Books"), "1953-10-05", 30.22, this.browsingGenres, "book-image.png"),
    new Book(5, "1983", new Author(1, "Orwell"), new Category(1, "Fiction"), "Anti-utopy", "21938432", new Publisher(1, "World Books"), "1953-10-05", 30.22, this.browsingGenres, "book-image.png"),
  ];

  getBooks(): Book[] {
    return this.popularBooks;
  }

  getBookById(id: number): Book | undefined {
    return this.popularBooks.find(book => book.id === id);
  }
}
