import {Author} from './author';
import {Category} from './category';
import {Publisher} from './publisher';
import {Genre} from './genre';

export class Book {
  constructor(
    public id?: number,
    public title?: string,
    public author?: Author,
    public category?: Category,
    public description?: string,
    public isbn?: string,
    public publisher?: Publisher,
    public releaseDate?: string,
    public price?: number,
    public bookGenres?: Genre[],
    public imageUrl?: string,
    public averageRating?: number,
    public totalReviews?: number
  ) {
  }

  public static fromObject(book: Book) {
    return new Book(
      book.id,
      book.title,
      book.author,
      book.category,
      book.description,
      book.isbn,
      book.publisher,
      book.releaseDate,
      book.price,
      book.bookGenres,
      book.imageUrl,
      book.averageRating,
      book.totalReviews,
    );
  }
}
