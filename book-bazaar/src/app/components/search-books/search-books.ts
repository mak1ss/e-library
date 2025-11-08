import { Component, effect, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatFormField, MatInput } from '@angular/material/input';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { FilterPanel } from '../filter-panel/filter-panel';
import { Book } from '../../model/book';
import { Filter } from '../../utils/filter';
import { BookService } from '../../services/book/book-service';
import { BookCard } from "../book-card/book-card";
import { AuthorService } from '../../services/author/author-service';
import { GenreService } from '../../services/genre/genre-service';
import { CategoryService } from '../../services/category/category-service';
import { PublisherService } from '../../services/publisher/publisher-service';

@Component({
  selector: 'app-search-books',
  imports: [
    MatFormField,
    ReactiveFormsModule,
    MatInput,
    MatButton,
    FilterPanel,
    BookCard
  ],
  templateUrl: './search-books.html',
  styleUrl: './search-books.css',
})
export class SearchBooks {

  popularBooks: Book[];

  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private authorService = inject(AuthorService);
  private genreService = inject(GenreService);
  private categoryService = inject(CategoryService);
  private publisherService = inject(PublisherService);

  query = '';

  formGroup: FormGroup = new FormGroup({
    search: new FormControl('')
  })

  selectedFilters = signal<Record<string, string[]>>({});

  effect = effect(() => {
    console.log(this.selectedFilters());
  });

  filterOptions: Filter[] = [];

  constructor(bookService: BookService) {
    this.popularBooks = bookService.getBooks();

    this.filterOptions.push(
      {
        name: 'author',
        label: 'Author',
        options: this.authorService.getAuthors().map(a => a.name),
        defaultVisibleCount: 4,
        expanded: false
      } as Filter,
      {
        name: 'genre',
        label: 'Genre',
        options: this.genreService.getGenres().map(g => g.name),
        defaultVisibleCount: 4,
        expanded: false
      } as Filter,
      {
        name: 'category',
        label: 'Category',
        options: this.categoryService.getCategories().map(c => c.name),
        defaultVisibleCount: 4,
        expanded: false
      } as Filter,
      {
        name: 'publisher',
        label: 'Publisher',
        options: this.publisherService.getPublishers().map(p => p.name),
        defaultVisibleCount: 4,
        expanded: false
      } as Filter
    );
  }

  ngOnInit(): void {
    this.route.queryParamMap.subscribe(params => {
      this.query = params.get('query') ?? '';

      this.formGroup.patchValue({ search: this.query }, { emitEvent: false });

      const filters: Record<string, string[]> = {};

      this.filterOptions.forEach(f => {
        const values = params.getAll(f.name) ?? [];
        if (values.length) filters[f.name] = values;
      });

      this.selectedFilters.set(filters);
    })
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

    console.log('Navigating with query params:', output, qp);

    if (this.query) qp['query'] = this.query;
    // merge with existing query params (and remove empty ones)
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: qp,
      queryParamsHandling: 'replace'
    });
  }
}
