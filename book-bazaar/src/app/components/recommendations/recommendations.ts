import { Component, DestroyRef, inject, Injector, OnInit, signal } from '@angular/core';
import { RouterModule } from '@angular/router';
import { forkJoin, Observable, of } from 'rxjs';
import { catchError, filter, map, switchMap, take } from 'rxjs/operators';
import { toObservable, takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { Book } from '../../model/book';
import { Review } from '../../model/review';
import { BookService } from '../../services/book/book-service';
import { ReviewService } from '../../services/review/review-service';
import { UserService } from '../../services/user/userService';
import { BookCard } from '../book-card/book-card';

type ReviewSection = {
  review: Review;
  book: Book;
  recommendations: Book[];
};

@Component({
  selector: 'app-recommendations',
  standalone: true,
  imports: [RouterModule, MatButtonModule, MatIconModule, MatTooltipModule, BookCard],
  templateUrl: './recommendations.html',
  styleUrl: './recommendations.css',
})
export class RecommendationsPage implements OnInit {
  private reviewService = inject(ReviewService);
  private bookService = inject(BookService);
  private injector = inject(Injector);
  private destroyRef = inject(DestroyRef);
  protected userService = inject(UserService);

  sections = signal<ReviewSection[]>([]);
  collaborativeBooks = signal<Book[]>([]);
  popularBooks = signal<Book[]>([]);
  isLoading = signal<boolean>(true);

  protected readonly starsArray = [1, 2, 3, 4, 5];
  protected readonly skeletonSections = [1, 2, 3];
  protected readonly skeletonCards = [1, 2, 3, 4, 5, 6];

  ngOnInit(): void {
    if (!this.userService.isLoggedIn()) {
      this.loadPopularBooks();
      this.isLoading.set(false);
      return;
    }

    toObservable(this.userService.userProfile, { injector: this.injector }).pipe(
      filter(profile => !!profile?.id),
      take(1),
      switchMap(profile =>
        this.reviewService.getReviewsByUserId(profile!.id!, 0, 50, 'rating,desc').pipe(
          catchError(() => of({ items: [] as Review[], total: 0 })),
          switchMap(page => {
            const eligible = page.items.filter(r => r.rating >= 3).slice(0, 5);
            const reviewedBookIds = new Set(page.items.map(r => r.bookId));

            if (eligible.length === 0) {
              return of({ sections: [] as ReviewSection[], collaborative: [] as Book[] });
            }

            return forkJoin({
              sections: this.buildSections(eligible, reviewedBookIds),
              collaborative: this.bookService.getPersonalizedRecommendations(10).pipe(
                map(p => p.items),
                catchError(err => {
                  console.warn('[Recommendations] Collaborative filtering failed:', err?.status, err?.message);
                  return of([] as Book[]);
                })
              ),
            });
          })
        )
      ),
      catchError(() => of({ sections: [] as ReviewSection[], collaborative: [] as Book[] })),
      takeUntilDestroyed(this.destroyRef)
    ).subscribe(({ sections, collaborative }) => {
      this.sections.set(sections);
      this.collaborativeBooks.set(collaborative);
      this.isLoading.set(false);
      if (sections.length === 0) this.loadPopularBooks();
    });
  }

  private buildSections(reviews: Review[], reviewedBookIds: Set<number>): Observable<ReviewSection[]> {
    return forkJoin(
      reviews.map(review =>
        forkJoin({
          book: this.bookService.getBookById(review.bookId).pipe(
            catchError(() => of(null as Book | null))
          ),
          recs: this.bookService.getSimilarBooks(review.bookId, 12).pipe(
            map(p => p.items.filter(b => !reviewedBookIds.has(b.id!)).slice(0, 6)),
            catchError(() => of([] as Book[]))
          ),
        }).pipe(
          map(({ book, recs }) => ({ review, book, recommendations: recs }))
        )
      )
    ).pipe(
      map(raw => raw.filter((s): s is ReviewSection => s.book !== null)),
      catchError(() => of([] as ReviewSection[]))
    );
  }

  private loadPopularBooks(): void {
    this.bookService.getBooks({}, 0, 10, 'totalReviews,desc')
      .subscribe({ next: p => this.popularBooks.set(p.items), error: () => {} });
  }

  protected getCollabReason(book: Book): string {
    return (book as any).explanation?.primaryReason ?? '';
  }
}
