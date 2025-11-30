import { Component, effect, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatFormField, MatInput } from '@angular/material/input';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { MatPaginatorModule, PageEvent } from '@angular/material/paginator';
import { FilterPanel } from '../filter-panel/filter-panel';
import { Book } from '../../model/book';
import { Filter } from '../../utils/filter';
import { BookService } from '../../services/book/book-service';
import { BookCard } from "../book-card/book-card";
import { AuthorService } from '../../services/author/author-service';
import { GenreService } from '../../services/genre/genre-service';
import { CategoryService } from '../../services/category/category-service';
import { PublisherService } from '../../services/publisher/publisher-service';
import { combineLatest, forkJoin, map, Observable } from 'rxjs';
import { Category } from '../../model/category';
import { Author } from '../../model/author';
import { Genre } from '../../model/genre';
import { Publisher } from '../../model/publisher';
import { PAGE_UP } from '@angular/cdk/keycodes';

@Component({
  selector: 'app-search-books',
  imports: [
    MatFormField,
    ReactiveFormsModule,
    MatInput,
    MatButton,
    FilterPanel,
    BookCard,
    MatPaginatorModule
  ],
  templateUrl: './search-books.html',
  styleUrl: './search-books.css',
})
export class SearchBooks {

  books = signal<Book[]>([]);
  totalBooks = signal<number>(0);
  loading = signal<boolean>(false);
  pageIndex = signal<number>(0);
  pageSize = signal<number>(20);

  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private authorService = inject(AuthorService);
  private genreService = inject(GenreService);
  private categoryService = inject(CategoryService);
  private publisherService = inject(PublisherService);
  private bookService = inject(BookService);

  query = '';

  formGroup: FormGroup = new FormGroup({
    search: new FormControl('')
  })

  selectedFilters = signal<Record<string, string[]>>({});

  effect = effect(() => {
    console.log(this.selectedFilters());
  });

  filterOptions = signal<Filter[]>([]);

  ngOnInit(): void {
    const filters$ = this.loadFilters();
    
    const params$ = this.route.queryParamMap;

    combineLatest([filters$, params$]).subscribe({
      next: ([filters, params]) => {
        this.filterOptions.set(filters);
        this.loading.set(true);

        const page = Number(params.get('page') ?? 0);
        const size = Number(params.get('size') ?? 20);
        
        this.pageIndex.set(page);
        this.pageSize.set(size);

        this.query = params.get('query') ?? '';
        this.formGroup.patchValue({ search: this.query }, { emitEvent: false });

        const activeFilters: Record<string, any> = {};

        if (this.query) {
          activeFilters['query'] = this.query;
        }

        filters.forEach(f => {
          const values = params.getAll(f.name);
          if (values && values.length > 0) {
            activeFilters[f.name] = values;
          }
        });

        this.selectedFilters.set(activeFilters as Record<string, string[]>);

        this.bookService.getBooks(activeFilters, page, size).subscribe({
          next: (response) => {
            this.books.set(response.items);
            this.totalBooks.set(response.total);
            this.loading.set(false);
          },
          error: (err) => {
            console.error('Error fetching books:', err);
            this.books.set([]);
            this.loading.set(false);
          }
        });
      },
      error: (err: any) => console.error('Error initializing search page:', err)
    });
  }

  private loadFilters(): Observable<Filter[]> {
    return forkJoin({
      authors: this.authorService.getAuthors(0, 20),
      genres: this.genreService.getGenres(0, 20),
      categories: this.categoryService.getCategories(0, 20),
      publishers: this.publisherService.getPublishers(0, 20)
    }).pipe(
      map((res: { authors: { items: any; }; genres: { items: any; }; categories: { items: any; }; publishers: { items: any; }; }) => {
        return [
          {
            name: 'author',
            label: 'Author',
            options: (res.authors.items || []).map((a: Author) => a.name || ''),
            defaultVisibleCount: 4, 
            expanded: false
          },
          {
            name: 'genre',
            label: 'Genre',
            options: (res.genres.items || []).map((g: Genre) => g.name || ''),
            defaultVisibleCount: 4,
            expanded: false
          },
          {
            name: 'category',
            label: 'Category',
            options: (res.categories.items || []).map((c: Category) => c.name || ''),
            defaultVisibleCount: 4,
            expanded: false
          },
          {
            name: 'publisher',
            label: 'Publisher',
            options: (res.publishers.items || []).map((p: Publisher) => p.name || ''),
            defaultVisibleCount: 4,
            expanded: false
          }
        ];
      })
    );
  }

  protected search(): void {
    this.query = this.formGroup.value.search ?? null;

    this.router.navigate([], {
      queryParams: { query: this.query },
      relativeTo: this.route,
      queryParamsHandling: 'merge'
    })
  }

  onFiltersChanged(output: Record<string, string[]>): void {
    this.selectedFilters.set(output);

    const qp: Record<string, any> = {};
    Object.entries(output).forEach(([k, v]) => {
      if (v && v.length) qp[k] = v; // arrays become repeated params
      else qp[k] = null; // remove empty params
    });

    qp['page'] = 0;
    
    console.log('Navigating with query params:', output, qp);
    
    if (this.query) qp['query'] = this.query;
    // merge with existing query params (and remove empty ones)
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: qp,
      queryParamsHandling: 'replace'
    });
  }

  onPageChange(event: PageEvent): void {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: { 
        page: event.pageIndex, 
        size: event.pageSize 
      },
      queryParamsHandling: 'merge'
    }).then(() => {
      this.scrollToResults();
    });
  }

  private scrollToResults(): void {
    const element = document.getElementById('search');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }
}
