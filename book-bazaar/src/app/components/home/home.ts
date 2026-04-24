import { Component, inject, signal, OnInit } from '@angular/core';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { Genre } from '../../model/genre';
import { MatRipple } from '@angular/material/core';
import { MatButton } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Book } from '../../model/book';
import { BookService } from '../../services/book/book-service';
import { BookCard } from "../book-card/book-card";
import { GenreService } from '../../services/genre/genre-service';
import { debounceTime, distinctUntilChanged, switchMap, filter, tap, catchError } from 'rxjs/operators';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { of } from 'rxjs';
import { CurrencyPipe, DecimalPipe } from '@angular/common';
import { MatIcon } from "@angular/material/icon";
import { UserService } from '../../services/user/userService';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

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
    MatIcon,
    MatTooltipModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home implements OnInit {
  protected router = inject(Router);
  protected bookService = inject(BookService);
  protected genreService = inject(GenreService);
  protected userService = inject(UserService);

  protected formGroup: FormGroup = new FormGroup(
    {
      search: new FormControl('')
    }
  );

  protected browsingGenres = signal<Genre[]>([]);
  protected popularBooks = signal<Book[]>([]);

  // Personalized recommendations
  protected recommendedBooks = signal<Book[]>([]);
  protected isLoadingRecommendations = signal<boolean>(false);
  protected recommendationType = signal<'personal' | 'popular'>('popular');

  protected liveSearchResults = signal<Book[]>([]);
  protected showDropdown = signal<boolean>(false);

  constructor() {
    this.setupLiveSearch();
  }

  ngOnInit() {
    this.loadRecommendations();
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

  /**
   * Load personalized recommendations (if logged in) or popular books (if not)
   */
  protected loadRecommendations(): void {
    this.isLoadingRecommendations.set(true);

    if (this.userService.isLoggedIn()) {
      // Logged in: try to get personalized recommendations
      this.bookService.getPersonalizedRecommendations(10).subscribe({
        next: (response) => {
          this.recommendedBooks.set(response.items || []);
          this.recommendationType.set('personal');
          this.isLoadingRecommendations.set(false);
        },
        error: (error) => {
          console.warn('Could not load personalized recommendations:', error);
          // Fallback to popular books
          this.loadPopularBooks();
        }
      });
    } else {
      // Not logged in: load popular books
      this.loadPopularBooks();
    }
  }

  /**
   * Load popular books (fallback for new/unauthenticated users)
   */
  protected loadPopularBooks(): void {
    this.bookService.getBooks({}, 0, 10)
      .subscribe({
        next: (response) => {
          this.recommendedBooks.set(response.items || []);
          this.recommendationType.set('popular');
          this.isLoadingRecommendations.set(false);
        },
        error: (error) => {
          console.error('Error loading popular books:', error);
          this.recommendedBooks.set([]);
          this.isLoadingRecommendations.set(false);
        }
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

  /**
   * Get recommendation reason for tooltip display
   */
  protected getRecommendationReason(book: Book): string {
    const bookWithExplanation = book as any;

    if (bookWithExplanation.explanation?.primaryReason) {
      const explanation = bookWithExplanation.explanation;
      return explanation.primaryReason;
    }

    // Fallback message
    return this.recommendationType() === 'personal'
      ? 'Recommended for you'
      : 'Popular book';
  }
}
