import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { map } from 'rxjs';
import { toSignal } from '@angular/core/rxjs-interop';
import { Author } from '../../model/author';
import { Book } from '../../model/book';
import { AuthorService } from '../../services/author/author-service';
import { BookService } from '../../services/book/book-service';
import { BookCard } from '../book-card/book-card';

const AVATAR_GRADIENTS = [
  ['#8b5cf6', '#7c3aed'],
  ['#3b82f6', '#4338ca'],
  ['#10b981', '#0d9488'],
  ['#f97316', '#d97706'],
  ['#f43f5e', '#db2777'],
  ['#06b6d4', '#0284c7'],
];

@Component({
  selector: 'app-author-details',
  imports: [
    RouterLink,
    MatButtonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatPaginatorModule,
    BookCard,
  ],
  templateUrl: './author-details.html',
  styleUrl: './author-details.css',
})
export class AuthorDetails {
  author = signal<Author | null>(null);
  books = signal<Book[]>([]);
  totalBooks = signal<number>(0);
  loading = signal<boolean>(true);
  booksLoading = signal<boolean>(false);
  pageIndex = signal<number>(0);
  pageSize = signal<number>(12);

  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private authorService = inject(AuthorService);
  private bookService = inject(BookService);

  private authorId = toSignal(
    this.route.paramMap.pipe(map(p => Number(p.get('authorId'))))
  );

  ngOnInit(): void {
    const id = this.authorId();
    if (id && id > 0) {
      this.loadAuthor(id);
    }
  }

  private loadAuthor(id: number): void {
    this.loading.set(true);
    this.authorService.getAuthorById(id).subscribe({
      next: (author) => {
        this.author.set(author);
        this.loading.set(false);
        this.loadBooks(author.name!);
      },
      error: () => {
        this.loading.set(false);
      },
    });
  }

  loadBooks(authorName: string): void {
    this.booksLoading.set(true);
    this.bookService
      .getBooks({ author: authorName }, this.pageIndex(), this.pageSize(), 'title,asc')
      .subscribe({
        next: (response) => {
          this.books.set(response.items);
          this.totalBooks.set(response.total);
          this.booksLoading.set(false);
        },
        error: () => {
          this.books.set([]);
          this.booksLoading.set(false);
        },
      });
  }

  onPageChange(event: PageEvent): void {
    this.pageIndex.set(event.pageIndex);
    this.pageSize.set(event.pageSize);
    if (this.author()?.name) {
      this.loadBooks(this.author()!.name!);
    }
  }

  browseAllBooks(): void {
    this.router.navigate(['/search'], { queryParams: { author: this.author()?.name } });
  }

  getInitials(name: string = ''): string {
    return name
      .split(' ')
      .slice(0, 2)
      .map(w => w[0]?.toUpperCase() ?? '')
      .join('');
  }

  getAvatarStyle(name: string = ''): string {
    const [from, to] = AVATAR_GRADIENTS[name.charCodeAt(0) % AVATAR_GRADIENTS.length];
    return `background: linear-gradient(135deg, ${from}, ${to})`;
  }
}
