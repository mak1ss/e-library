import { Component, inject, signal, OnInit } from '@angular/core';
import { MatFormField } from '@angular/material/input';
import { MatInput } from '@angular/material/input';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { Genre } from '../../model/genre';
import { MatRipple } from '@angular/material/core';
import { MatButton } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Book } from '../../model/book';
import { BookService } from '../../services/book/book-service';
import { BookCard } from "../book-card/book-card";
import { GenreService } from '../../services/genre/genre-service';
import { UserService } from '../../services/user/userService';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { CurrencyPipe } from '@angular/common';

@Component({
  selector: 'app-home',
  imports: [
    MatFormField,
    MatInput,
    ReactiveFormsModule,
    MatRipple,
    MatButton,
    MatTooltipModule,
    BookCard,
    MatProgressSpinnerModule,
    CurrencyPipe
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

  ngOnInit() {
    this.loadRecommendations();
    this.genreService.getGenres(0, 6)
      .subscribe(page => this.browsingGenres.set(page.items));
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

    this.router.navigate(['/search'], { queryParams: { query: filter } });
  }

  protected searchByGenre(genre: Genre) {
    this.router.navigate(['/search'], { queryParams: { genre: genre.name } });
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


