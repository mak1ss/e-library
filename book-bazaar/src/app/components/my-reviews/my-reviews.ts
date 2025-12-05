import { Component, inject, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

import { UserService } from '../../services/user/userService';
import { Review } from '../../model/review';
import { UserReviewCard } from '../user-review-card/user-review-card';
import { ReviewService } from '../../services/review/review-service';
import { MatMenuModule } from '@angular/material/menu';
@Component({
  selector: 'app-my-reviews',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatFormFieldModule, 
    MatSelectModule, 
    MatIconModule,
    MatButtonModule,
    MatPaginatorModule,
    MatProgressSpinnerModule,
    UserReviewCard,
    MatMenuModule
  ],
  templateUrl: './my-reviews.html',
})
export class MyReviews implements OnInit {
  private reviewService = inject(ReviewService);
  private userService = inject(UserService);
  private router = inject(Router);

  reviews = signal<Review[]>([]);
  totalReviews = signal<number>(0);
  loading = signal<boolean>(true);

  // Стан
  pageIndex = signal<number>(0);
  pageSize = signal<number>(10);
  sort = signal<string>('createdAt,desc');

  ngOnInit() {
    this.loadReviews();
  }

  loadReviews() {
    const user = this.userService.userProfile();
    if(!user) {
      this.loading.set(false);
      return;
    }
    const userId = user.id;
    this.loading.set(true);
    this.reviewService.getReviewsByUserId(
      userId!, 
      this.pageIndex(), 
      this.pageSize(), 
      this.sort()
    ).subscribe({
      next: (page) => {
        this.reviews.set(page.items);
        this.totalReviews.set(page.total);
        this.loading.set(false);
      },
      error: (err) => {
        console.error(err);
        this.loading.set(false);
      }
    });
  }

  onSortChange(newSort: string) {
    this.sort.set(newSort);
    this.pageIndex.set(0);
    this.loadReviews();
  }

  onPageChange(e: PageEvent) {
    this.pageIndex.set(e.pageIndex);
    this.pageSize.set(e.pageSize);
    this.loadReviews();
  }

  handleEdit(review: Review) {
    this.router.navigate(['/book-details', review.bookId, 'review']);
  }

  handleDelete(reviewId: string) {
    this.reviewService.deleteReview(reviewId).subscribe({
      next: () => {
        this.reviews.update(list => list.filter(r => r.id !== reviewId));
        this.totalReviews.update(t => t - 1);
      },
      error: (err) => console.error('Delete failed', err)
    });
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