import { Injectable } from '@angular/core';
import { Genre } from '../../model/genre';

@Injectable({
  providedIn: 'root',
})
export class GenreService {
  genres: Genre[] = [
    new Genre(1, "Comedy"),
    new Genre(2, "Romance"),
    new Genre(3, "Adventure"),
    new Genre(4, "Business"),
    new Genre(5, "Science Fiction"),
    new Genre(6, "Fantasy"),
    new Genre(7, "Horror"),
    new Genre(8, "Thriller"),
    new Genre(9, "Non-Fiction"),
    new Genre(10, "Biography"),
  ];

  getGenres(): Genre[] {
    return this.genres;
  }
}
