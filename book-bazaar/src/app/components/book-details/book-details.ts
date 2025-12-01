import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
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
import {MatSelectModule} from '@angular/material/select';
import { DatePipe, CurrencyPipe, NgClass, DecimalPipe } from '@angular/common'

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
    NgClass
],
  templateUrl: './book-details.html',
  styleUrl: './book-details.css',
})
export class BookDetails implements OnInit {
  private route = inject(ActivatedRoute);
  private bookService = inject(BookService);
  private reviewService = inject(ReviewService);
  
  book = signal<Book | null>(null);
  loading = signal<boolean>(true);

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
    this.userRating.set(star);
    console.log(`User rated: ${star}`);
  }

  setHoverRating(star: number) {
    this.hoverRating.set(star);
  }

  clearHoverRating() {
    this.hoverRating.set(0);
  }

  writeReview() {
    console.log('Open review dialog');
  }
}