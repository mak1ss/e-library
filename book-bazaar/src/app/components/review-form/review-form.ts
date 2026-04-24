import { Component, inject, OnInit, signal, computed } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';
import { BookService } from '../../services/book/book-service';
import { UserService } from '../../services/user/userService';
import { Review } from '../../model/review';
import { Book } from '../../model/book';
import { NgClass, Location } from '@angular/common';
import { ReviewService } from '../../services/review/review-service';

@Component({
  selector: 'app-review-form',
  standalone: true,
  imports: [ReactiveFormsModule, MatFormFieldModule, MatInputModule, MatButtonModule, MatIconModule, MatTooltipModule, NgClass],
  templateUrl: './review-form.html',
})
export class ReviewForm implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private fb = inject(FormBuilder);
  private reviewService = inject(ReviewService);
  private bookService = inject(BookService);
  private userService = inject(UserService);
  private location = inject(Location);
  
  bookId = signal<number>(0);
  book = signal<Book | null>(null);
  existingReview = signal<Review | null>(null);

  form = this.fb.group({
    rating: [0, [Validators.required, Validators.min(1), Validators.max(5)]],
    text: ['', [Validators.maxLength(1000)]]
  });

  get ratingLabel(): string {
    const rating = this.form.value.rating || 0;
    switch (rating) {
      case 1: return 'Terrible';
      case 2: return 'Bad';
      case 3: return 'Average';
      case 4: return 'Good';
      case 5: return 'Amazing!';
      default: return 'Select your rating';
    }
  }

  // Тексти підказок для тултипів
  ratingTooltips = ['Terrible', 'Bad', 'Average', 'Good', 'Amazing!'];

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('bookId');
    if (id) {
      this.bookId.set(Number(id));
      this.loadData();
    }
  }

  async loadData() {
    this.bookService.getBookById(this.bookId()).subscribe(b => this.book.set(b));

    const user = this.userService.userProfile();
    if (user) {
      const userId = user.id;
      this.reviewService.getUserReview(this.bookId(), userId!).subscribe(review => {
        if (review) {
          this.existingReview.set(review);
          this.form.patchValue({
            rating: review.rating,
            text: review.text
          });
        }
      });
    }
  }

  setRating(star: number) {
    this.form.controls.rating.setValue(star);
    this.form.controls.rating.markAsTouched();
  }

  submit() {
    if (this.form.invalid) return;

    const request = {
      bookId: this.bookId(),
      rating: this.form.value.rating!,
      text: this.form.value.text || ''
    };

    const review = this.existingReview();

    const obs$ = review
      ? this.reviewService.updateReview(review.id, request)
      : this.reviewService.createReview(request);

    obs$.subscribe({
      next: () => this.location.back(),
      error: (err) => console.error('Failed to save review', err)
    });
  }

  cancel() {
    this.location.back();
  }

  get hasUnsavedChanges(): boolean {
    const initial = this.existingReview();
    const currentRating = this.form.value.rating ?? 0;
    const currentText = this.form.value.text ?? '';

    if (initial) {
      return currentRating !== initial.rating || currentText.trim() !== (initial.text || '').trim();
    } else {
      return currentRating !== 0 || currentText.trim().length > 0;
    }
  }
}