import { Component, input, inject, OnInit, signal, output } from '@angular/core';
import { CommonModule, DatePipe } from '@angular/common';
import { RouterModule } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { Review } from '../../model/review';
import { Book } from '../../model/book';
import { BookService } from '../../services/book/book-service';

@Component({
  selector: 'app-user-review-card',
  standalone: true,
  imports: [
    CommonModule, 
    RouterModule, 
    MatCardModule, 
    MatIconModule, 
    MatButtonModule, 
    MatMenuModule,
    DatePipe
  ],
  templateUrl: './user-review-card.html'
})
export class UserReviewCard implements OnInit {
  review = input.required<Review>();
  
  // Події для батьківського компонента
  onDelete = output<string>();
  onEdit = output<Review>();

  private bookService = inject(BookService);
  
  book = signal<Book | null>(null);
  loadingBook = signal<boolean>(true);

  ngOnInit() {
    this.bookService.getBookById(this.review().bookId).subscribe({
      next: (b) => {
        this.book.set(b);
        this.loadingBook.set(false);
      },
      error: () => this.loadingBook.set(false)
    });
  }

  delete() {
    if (confirm('Are you sure you want to delete this review?')) {
      this.onDelete.emit(this.review().id);
    }
  }

  edit() {
    this.onEdit.emit(this.review());
  }
}