import { Component, inject, signal } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { Genre } from '../../model/genre';
import { MatRipple } from '@angular/material/core';
import { MatButton } from '@angular/material/button';
import { Book } from '../../model/book';
import { BookService } from '../../services/book/book-service';
import { BookCard } from "../book-card/book-card";
import { GenreService } from '../../services/genre/genre-service';
import { debounceTime, distinctUntilChanged, switchMap, filter, tap, catchError } from 'rxjs/operators';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { of } from 'rxjs';
import { CurrencyPipe, DecimalPipe } from '@angular/common';
import { MatIcon } from "@angular/material/icon";

@Component({
  selector: 'app-home',
  imports: [
    ReactiveFormsModule,
    MatRipple,
    MatButton,
    BookCard,
    CurrencyPipe,
    DecimalPipe,
    RouterModule,
    MatIcon
],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home {
  protected router = inject(Router);
  protected bookService = inject(BookService);
  protected genreService = inject(GenreService);
  protected formGroup: FormGroup = new FormGroup(
    {
      search: new FormControl('')
    }
  );

  protected browsingGenres = signal<Genre[]>([]);
  protected popularBooks = signal<Book[]>([]);

  protected liveSearchResults = signal<Book[]>([]);
  protected showDropdown = signal<boolean>(false);

  constructor() {
    this.setupLiveSearch();
  }

  ngOnInit() {
    this.bookService.getBooks({}, 0, 5)
      .subscribe(page => this.popularBooks.set(page.items));
    this.genreService.getGenres(0, 6)
      .subscribe(page => this.browsingGenres.set(page.items));
  }

  private setupLiveSearch() {
    this.formGroup.get('search')?.valueChanges.pipe(
      debounceTime(300), // Чекаємо 300мс
      distinctUntilChanged(),
      tap(val => {
        // Якщо поле очистили - ховаємо дропдаун
        if (!val) {
          this.showDropdown.set(false);
          this.liveSearchResults.set([]);
        }
      }),
      // Фільтруємо пусті запити, щоб не слати зайве на сервер
      filter(val => !!val && val.length > 1),
      switchMap(query => {
        // Використовуємо наш сервіс з параметром q (який ми налаштували раніше)
        // Запитуємо лише 5 книг для прев'ю
        return this.bookService.getBooks({ query: query }, 0, 5).pipe(
          // Якщо сталась помилка, повертаємо пустий масив, щоб не ламати потік
          catchError(() => of({ items: [], total: 0 }))
        );
      }),
      takeUntilDestroyed()
    ).subscribe(response => {
      // @ts-ignore (якщо у вас strict mode і catchError повертає не зовсім PaginatedResult)
      const books = response.items || [];
      this.liveSearchResults.set(books);
      this.showDropdown.set(books.length > 0);
    });
  }

  protected search() {
    let filter = this.formGroup.value.search;
    if (!filter) return;
    this.showDropdown.set(false);
    this.router.navigate(['/search'], { queryParams: { query: filter } });
  }

  protected searchByGenre(genre: Genre) {
    this.router.navigate(['/search'], { queryParams: { genre: genre.name } });
  }

  closeDropdown() {
    setTimeout(() => this.showDropdown.set(false), 200);
  }
}
