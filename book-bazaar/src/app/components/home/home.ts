import { Component, inject } from '@angular/core';
import { MatFormField } from '@angular/material/input';
import { MatInput } from '@angular/material/input';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Genre } from '../../model/genre';
import { MatRipple } from '@angular/material/core';
import { MatButton } from '@angular/material/button';
import { Book } from '../../model/book';
import { BookService } from '../../services/book/book-service';
import { BookCard } from "../book-card/book-card";
import { GenreService } from '../../services/genre/genre-service';

@Component({
  selector: 'app-home',
  imports: [
    MatFormField,
    MatInput,
    ReactiveFormsModule,
    MatRipple,
    MatButton,
    BookCard
  ],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home {
  protected router = inject(Router);

  protected formGroup: FormGroup = new FormGroup(
    {
      search: new FormControl('')
    }
  );

  protected browsingGenres: Genre[];

  popularBooks: Book[];

  constructor(
    bookService: BookService,
    genreService: GenreService
  ) {
    this.popularBooks = bookService.getBooks().slice(0, 5);
    this.browsingGenres = genreService.getGenres().slice(0, 4);
  }

  protected search() {
    let filter = this.formGroup.value.search;
    if (!filter) return;

    this.router.navigate(['/search'], { queryParams: { query: filter } });
  }

  protected searchByGenre(genre: Genre) {
    this.router.navigate(['/search'], { queryParams: { genre: genre.name } });
  }
}
