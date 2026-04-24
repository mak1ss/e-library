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
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { ConfirmDialog } from '../dialog/confirm-dialog';

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
    DatePipe,
    MatDialogModule
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
  private dialog = inject(MatDialog);

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
    // 5. Викликаємо діалог замість confirm()
    const dialogRef = this.dialog.open(ConfirmDialog, {
      width: '400px',
      enterAnimationDuration: '200ms',
      exitAnimationDuration: '200ms',
      // panelClass дозволяє нам стилізувати контейнер діалогу глобально (див. Крок 3)
      panelClass: 'custom-dialog-container' 
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        this.onDelete.emit(this.review().id);
      }
    });
  }
  
  edit() {
    this.onEdit.emit(this.review());
  }
}