import { Injectable } from '@angular/core';
import { Author } from '../../model/author';

@Injectable({
  providedIn: 'root',
})
export class AuthorService {
  
  authors: Author[] = [
    new Author(1, "Rowling"),
    new Author(2, "Tolkien"),
    new Author(3, "Gaiman"),
    new Author(4, "George Orwell"),
    new Author(5, "Gaiman"),
    new Author(5, "Austen"),
    new Author(6, "King"),
  ];

  getAuthors(): Author[] {
    return this.authors;
  }
}
