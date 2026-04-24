import { Component, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormControl, ReactiveFormsModule } from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { MatProgressSpinner } from '@angular/material/progress-spinner';
import { MatMenuModule } from '@angular/material/menu';
import { combineLatest } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Author } from '../../model/author';
import { AuthorService } from '../../services/author/author-service';

const AVATAR_GRADIENTS = [
  ['#8b5cf6', '#7c3aed'],
  ['#3b82f6', '#4338ca'],
  ['#10b981', '#0d9488'],
  ['#f97316', '#d97706'],
  ['#f43f5e', '#db2777'],
  ['#06b6d4', '#0284c7'],
];

@Component({
  selector: 'app-authors',
  imports: [
    ReactiveFormsModule,
    MatButton,
    MatIcon,
    MatPaginatorModule,
    MatProgressSpinner,
    MatMenuModule,
  ],
  templateUrl: './authors.html',
  styleUrl: './authors.css',
})
export class AuthorsPage {
  authors = signal<Author[]>([]);
  totalAuthors = signal<number>(0);
  loading = signal<boolean>(false);
  pageIndex = signal<number>(0);
  pageSize = signal<number>(12);
  currentSort = signal<string>('name,asc');

  searchControl = new FormControl('');

  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private authorService = inject(AuthorService);

  constructor() {
    this.searchControl.valueChanges.pipe(
      debounceTime(500),
      distinctUntilChanged(),
      takeUntilDestroyed(),
    ).subscribe(value => {
      this.router.navigate([], {
        relativeTo: this.route,
        queryParams: { query: value || null, page: 0 },
        queryParamsHandling: 'merge',
      });
    });
  }

  ngOnInit(): void {
    combineLatest([this.route.queryParamMap]).subscribe({
      next: ([params]) => {
        const page = Number(params.get('page') ?? 0);
        const size = Number(params.get('size') ?? 12);
        const sort = params.get('sort') ?? 'name,asc';
        const query = params.get('query') ?? '';

        this.pageIndex.set(page);
        this.pageSize.set(size);
        this.currentSort.set(sort);
        this.searchControl.setValue(query, { emitEvent: false });

        this.loading.set(true);

        this.authorService.getAuthors(page, size, query || undefined, sort).subscribe({
          next: (response) => {
            this.authors.set(response.items);
            this.totalAuthors.set(response.total);
            this.loading.set(false);
          },
          error: () => {
            this.authors.set([]);
            this.loading.set(false);
          },
        });
      },
    });
  }

  onPageChange(event: PageEvent): void {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { page: event.pageIndex, size: event.pageSize },
      queryParamsHandling: 'merge',
    });
  }

  updateSort(sort: string): void {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { sort, page: 0 },
      queryParamsHandling: 'merge',
    });
  }

  openDetails(author: Author): void {
    this.router.navigate(['/authors', author.id]);
  }

  viewBooks(author: Author): void {
    this.router.navigate(['/search'], { queryParams: { author: author.name } });
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

  sortLabel(): string {
    return this.currentSort() === 'name,asc' ? 'A – Z' : 'Z – A';
  }
}
