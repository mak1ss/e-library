import { Component, inject, OnInit, signal, ViewChild } from '@angular/core';
import { MatTableModule } from '@angular/material/table';
import { MatPaginatorModule, MatPaginator, PageEvent } from '@angular/material/paginator';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { FormsModule } from '@angular/forms';
import { DecimalPipe } from '@angular/common';
import { debounceTime, distinctUntilChanged, of, Subject, switchMap } from 'rxjs';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Book } from '../../../model/book';
import { BookService } from '../../../services/book/book-service';
import { BookFormDialog, BookFormDialogData, BookFormDialogResult } from '../book-form-dialog/book-form-dialog';
import { ConfirmDialog } from '../../dialog/confirm-dialog';

@Component({
  selector: 'app-admin-books',
  standalone: true,
  imports: [
    MatTableModule, MatPaginatorModule, MatButtonModule, MatIconModule,
    MatInputModule, MatFormFieldModule, MatTooltipModule, MatDialogModule,
    MatProgressSpinnerModule, FormsModule, DecimalPipe,
  ],
  templateUrl: './admin-books.html',
})
export class AdminBooksPage implements OnInit {
  private bookService = inject(BookService);
  private dialog = inject(MatDialog);

  books = signal<Book[]>([]);
  total = signal(0);
  loading = signal(true);

  pageIndex = 0;
  pageSize = 10;
  searchQuery = '';

  readonly columns = ['title', 'author', 'category', 'price', 'averageRating', 'totalReviews', 'actions'];

  private search$ = new Subject<string>();

  constructor() {
    this.search$.pipe(
      debounceTime(400),
      distinctUntilChanged(),
      switchMap(q => {
        this.pageIndex = 0;
        this.loading.set(true);
        return this.bookService.getBooks(q ? { query: q } : {}, 0, this.pageSize, 'title,asc');
      }),
      takeUntilDestroyed(),
    ).subscribe(page => {
      this.books.set(page.items);
      this.total.set(Number(page.total));
      this.loading.set(false);
    });
  }

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.loading.set(true);
    const filters = this.searchQuery ? { query: this.searchQuery } : {};
    this.bookService.getBooks(filters, this.pageIndex, this.pageSize, 'title,asc').subscribe({
      next: page => {
        this.books.set(page.items);
        this.total.set(Number(page.total));
        this.loading.set(false);
      },
      error: () => this.loading.set(false),
    });
  }

  onSearch(value: string): void {
    this.search$.next(value);
  }

  onPage(event: PageEvent): void {
    this.pageIndex = event.pageIndex;
    this.pageSize = event.pageSize;
    this.load();
  }

  openCreate(): void {
    const ref = this.dialog.open(BookFormDialog, { data: {} as BookFormDialogData, disableClose: true });
    ref.afterClosed().subscribe((result: BookFormDialogResult | undefined) => {
      if (!result) return;
      this.bookService.createBook(result.request).pipe(
        switchMap(book => result.coverFile
          ? this.bookService.uploadCover(book.id!, result.coverFile)
          : of(book)
        ),
      ).subscribe(() => this.load());
    });
  }

  openEdit(book: Book): void {
    const ref = this.dialog.open(BookFormDialog, { data: { book } as BookFormDialogData, disableClose: true });
    ref.afterClosed().subscribe((result: BookFormDialogResult | undefined) => {
      if (!result) return;
      this.bookService.updateBook(book.id!, result.request).pipe(
        switchMap(updated => result.coverFile
          ? this.bookService.uploadCover(updated.id!, result.coverFile)
          : of(updated)
        ),
      ).subscribe(() => this.load());
    });
  }

  openDelete(book: Book): void {
    const ref = this.dialog.open(ConfirmDialog, { data: { title: 'Delete Book?', message: 'This action cannot be undone. Are you sure you want to remove this book permanently?' } });
    ref.afterClosed().subscribe(confirmed => {
      if (confirmed) this.bookService.deleteBook(book.id!).subscribe(() => this.load());
    });
  }
}
