import { Component, computed, effect, inject, signal } from '@angular/core';
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
import { MatIcon } from "@angular/material/icon";
import { MatProgressSpinner } from "@angular/material/progress-spinner";
import { MatSliderModule } from '@angular/material/slider';
import { MatMenuModule } from '@angular/material/menu';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-search-books',
  imports: [
    MatFormField,
    ReactiveFormsModule,
    MatInput,
    MatButton,
    FilterPanel,
    BookCard,
    MatPaginatorModule,
    MatIcon,
    MatProgressSpinner,
    MatSliderModule,
    MatMenuModule,
    FormsModule
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
  currentSort = signal<string>('title,asc');

  minPrice = signal<number | null>(null);
  maxPrice = signal<number | null>(null);

  minRating = signal<number | null>(null);

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
  hasAnyFilter = computed(() => {
    const hasPrice = this.minPrice() !== null || this.maxPrice() !== null;
    const hasRating = this.minRating() !== null;
    
    const currentFilters = this.selectedFilters();
    const hasDynamicFilters = Object.values(currentFilters)
      .some(arr => arr && arr.length > 0);

    return hasPrice || hasRating || hasDynamicFilters;
  });

  ngOnInit(): void {
    const filters$ = this.loadFilters();

    const params$ = this.route.queryParamMap;

    combineLatest([filters$, params$]).subscribe({
      next: ([filters, params]) => {
        this.filterOptions.set(filters);
        this.loading.set(true);

        const page = Number(params.get('page') ?? 0);
        const size = Number(params.get('size') ?? 20);
        const sortParam = params.get('sort') ?? 'title,asc';

        const minP = params.get('minPrice');
        const maxP = params.get('maxPrice');
        const minR = params.get('minRating');

        this.pageIndex.set(page);
        this.pageSize.set(size);
        this.currentSort.set(sortParam);

        this.minPrice.set(minP ? Number(minP) : null);
        this.maxPrice.set(maxP ? Number(maxP) : null);
        this.minRating.set(minR ? Number(minR) : null);

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

        if (this.minPrice()) activeFilters['minPrice'] = this.minPrice();
        if (this.maxPrice()) activeFilters['maxPrice'] = this.maxPrice();
        if (this.minRating()) activeFilters['minRating'] = this.minRating();

        this.selectedFilters.set(activeFilters as Record<string, string[]>);

        this.bookService.getBooks(activeFilters, page, size, this.currentSort()).subscribe({
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

  clearAllFilters(): void {
    this.minPrice.set(null);
    this.maxPrice.set(null);
    this.minRating.set(null);
    this.selectedFilters.set({});

    const resetParams: Record<string, any> = {
      minPrice: null,
      maxPrice: null,
      minRating: null,
      page: 0
    };

    this.filterOptions().forEach(f => {
      resetParams[f.name] = null;
    });

    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: resetParams,
      queryParamsHandling: 'merge'
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

  updateSort(newSort: string): void {
    this.updateQueryParams({ sort: newSort, page: 0 }); // Скидаємо на 1 сторінку при сортуванні
  }

  updatePrice(): void {
    this.updateQueryParams({
      minPrice: this.minPrice(),
      maxPrice: this.maxPrice(),
      page: 0
    });
  }

  updateRating(rating: number | null): void {
    // Якщо клікнули на той самий рейтинг - знімаємо фільтр
    const newValue = this.minRating() === rating ? null : rating;
    this.updateQueryParams({ minRating: newValue, page: 0 });
  }

  private updateQueryParams(params: Record<string, any>): void {
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: params,
      queryParamsHandling: 'merge' // Злиття з існуючими параметрами
    });
  }

  private scrollToResults(): void {
    const element = document.getElementById('search');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }
}
