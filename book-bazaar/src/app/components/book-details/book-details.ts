import { Component, inject, OnInit, signal } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { BookService } from '../../services/book/book-service';
import { Book } from '../../model/book';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { DatePipe, CurrencyPipe } from '@angular/common';

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
    CurrencyPipe
  ],
  templateUrl: './book-details.html',
  styleUrl: './book-details.css',
})
export class BookDetails implements OnInit {
  private route = inject(ActivatedRoute);
  private bookService = inject(BookService);

  book = signal<Book | null>(null);
  loading = signal<boolean>(true);

  // Для відображення рейтингу (поки що заглушка, пізніше підтягнемо з бекенду)
  rating = 4.4; 
  totalRatings = 1250;

  // Для інтерактивних зірок (What do you think?)
  userRating = signal<number>(0);
  hoverRating = signal<number>(0);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('bookId');
    if (id) {
      this.loadBook(Number(id));
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

  // Логіка для зірок
  setRating(star: number) {
    this.userRating.set(star);
    console.log(`User rated: ${star}`);
    // Тут буде виклик методу для збереження рейтингу
  }

  setHoverRating(star: number) {
    this.hoverRating.set(star);
  }

  clearHoverRating() {
    this.hoverRating.set(0);
  }

  writeReview() {
    console.log('Open review dialog');
    // Тут відкриємо діалог написання рецензії
  }
}