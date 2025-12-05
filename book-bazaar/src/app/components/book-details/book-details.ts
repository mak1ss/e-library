import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { BookService } from '../../services/book/book-service';
import { Book } from '../../model/book';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { ReviewService } from '../../services/review/review-service';
import { Review } from '../../model/review';
import { ReviewMetrics } from '../../model/review-metric';
import { PageEvent, MatPaginator } from '@angular/material/paginator';
import { MatFormField } from "@angular/material/input";
import { MatOption } from "@angular/material/core";
import { MatSelectModule } from '@angular/material/select';
import { DatePipe, CurrencyPipe, NgClass, DecimalPipe } from '@angular/common'
import { UserService } from '../../services/user/userService';
import { ReviewRequest } from '../../model/review-request';
import { MatMenuModule } from '@angular/material/menu';

@Component({
  selector: 'app-book-details',
  standalone: true,
  imports: [
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatDividerModule,
    MatProgressSpinnerModule,
    DatePipe,
    CurrencyPipe,
    MatPaginator,
    MatFormField,
    MatOption,
    MatSelectModule,
    DecimalPipe,
    NgClass,
    MatMenuModule
  ],
  templateUrl: './book-details.html',
  styleUrl: './book-details.css',
})
export class BookDetails implements OnInit {
  protected router = inject(Router);
  private route = inject(ActivatedRoute);
  private bookService = inject(BookService);
  private reviewService = inject(ReviewService);

  book = signal<Book | null>(null);
  loading = signal<boolean>(true);

  userService = inject(UserService); // Інжект юзера
  currentUserReview = signal<Review | null>(null);

  reviews = signal<Review[]>([]);
  metrics = signal<ReviewMetrics | null>(null);
  reviewsTotal = signal<number>(0);
  reviewsLoading = signal<boolean>(false);

  pageIndex = signal<number>(0);
  pageSize = signal<number>(10);
  currentSort = signal<string>('createdAt,desc');
  selectedRatingFilter = signal<number | undefined>(undefined);

  userRating = signal<number>(0);
  hoverRating = signal<number>(0);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('bookId');
    if (id) {
      const bookId = Number(id);
      this.loadBook(bookId);
      this.loadMetrics(bookId);
      this.loadReviews(bookId);
      this.checkUserReview(bookId);
    }
  }

  private loadBook(id: number) {
    this.loading.set(true);
    this.bookService.getBookById(id).subscribe({
      next: (data) => {
        this.book.set(data);
        this.loading.set(false);
      },
      error: (err) => {
        console.error(err);
        this.loading.set(false);
      }
    });
  }

  private loadMetrics(id: number) {
    this.reviewService.getBookMetrics(id).subscribe({
      next: (data) => this.metrics.set(data),
      error: () => console.log('No metrics found or error')
    });
  }

  loadReviews(bookId: number) {
    this.reviewsLoading.set(true);
    this.reviewService.getReviews(
      bookId,
      this.pageIndex(),
      this.pageSize(),
      this.currentSort(),
      this.selectedRatingFilter()
    ).subscribe({
      next: (page) => {
        this.reviews.set(page.items);
        this.reviewsTotal.set(page.total);
        this.reviewsLoading.set(false);
      },
      error: (err) => {
        console.error(err);
        this.reviewsLoading.set(false);
      }
    });
  }

  private checkUserReview(bookId: number) {
    if (this.userService.isLoggedIn()) {
      const user = this.userService.userProfile();
      if (user) {
        const userId = user.id;
        this.reviewService.getUserReview(bookId, userId!).subscribe({
          next: (review) => {
            this.currentUserReview.set(review);
            if (review) {
              this.userRating.set(review.rating); // Встановлюємо зірки
            }
          }
        });
      }
    }
  }

  onPageChange(event: PageEvent) {
    this.pageIndex.set(event.pageIndex);
    this.pageSize.set(event.pageSize);
    if (this.book()) {
      this.loadReviews(this.book()!.id!);
    }
  }

  onSortChange(sortValue: string) {
    this.currentSort.set(sortValue);
    this.pageIndex.set(0);
    if (this.book()) {
      this.loadReviews(this.book()!.id!);
    }
  }

  toggleRatingFilter(star: number) {
    // Якщо клікнули на вже вибраний фільтр - знімаємо його
    if (this.selectedRatingFilter() === star) {
      this.selectedRatingFilter.set(undefined);
    } else {
      this.selectedRatingFilter.set(star);
    }

    this.pageIndex.set(0);
    if (this.book()) {
      this.loadReviews(this.book()!.id!);
    }
  }

  getStarPercentage(star: number): number {
    const m = this.metrics();
    if (!m || m.totalReviews === 0) return 0;

    const count = m.reviewCountsRating[star.toString()] || 0;
    return (count / m.totalReviews) * 100;
  }

  getStarIcon(index: number): string {
    const rating = this.metrics()?.averageRating || 0;
    const rounded = Math.round(rating * 2) / 2;

    if (rounded >= index + 1) {
      return 'star';
    } else if (rounded >= index + 0.5) {
      return 'star_half';
    } else {
      return 'star_border';
    }
  }

  getStarCount(star: number): number {
    return this.metrics()?.reviewCountsRating[star.toString()] || 0;
  }

  setRating(star: number) {
    if (!this.userService.isLoggedIn()) {
      this.userService.login(); // Або показати повідомлення
      return;
    }

    this.userRating.set(star);

    const request: ReviewRequest = {
      bookId: this.book()!.id!,
      rating: star,
      text: this.currentUserReview()?.text || ''
    };

    const review = this.currentUserReview();

    const obs$ = review
      ? this.reviewService.updateReview(review.id, request)
      : this.reviewService.createReview(request);

    obs$.subscribe({
      next: (savedReview) => {
        this.currentUserReview.set(savedReview);
        console.log('Rating saved');
        this.loadMetrics(this.book()!.id!);
        this.loadReviews(this.book()!.id!)
      }
    });
  }

  writeReview() {
    if (!this.userService.isLoggedIn()) {
      this.userService.login();
      return;
    }
    this.router.navigate(['/book-details', this.book()?.id, 'review']);
  }

  setHoverRating(star: number) {
    this.hoverRating.set(star);
  }

  clearHoverRating() {
    this.hoverRating.set(0);
  }

  scrollToTarget(): void {
    const element = document.getElementById('reviews');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }

  getSortLabel(value: string): string {
    switch (value) {
      case 'createdAt,desc': return 'Newest first';
      case 'createdAt,asc': return 'Oldest first';
      case 'rating,desc': return 'Highest rated';
      case 'rating,asc': return 'Lowest rated';
      default: return 'Sort by';
    }
  }
}