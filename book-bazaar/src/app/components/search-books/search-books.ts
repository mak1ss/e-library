import { Component, effect, inject, signal } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { MatFormField, MatInput } from '@angular/material/input';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { MatButton } from '@angular/material/button';
import { FilterPanel } from '../filter-panel/filter-panel';
import { Book } from '../../model/book';
import { Publisher } from '../../model/publisher';
import { Genre } from '../../model/genre';
import { Filter } from '../../utils/filter';

@Component({
  selector: 'app-search-books',
  imports: [
    MatFormField,
    ReactiveFormsModule,
    MatInput,
    MatButton,
    FilterPanel
  ],
  templateUrl: './search-books.html',
  styleUrl: './search-books.css',
})
export class SearchBooks {

  browsingGenres: Genre[] = [
    new Genre(1, "Comedy"),
    new Genre(1, "Romance"),
    new Genre(1, "Adventure"),
    new Genre(1, "Business")
  ];

  popularBooks: Book[] = [
    new Book(1, "1983", "Orwell", "Fiction", "Anti-utopy", "21938432", new Publisher(1, "World Books"), "1953-10-05", 30.22, this.browsingGenres, "book-image.png"),
    new Book(1, "1983", "Orwell", "Fiction", "Anti-utopy", "21938432", new Publisher(1, "World Books"), "1953-10-05", 30.22, this.browsingGenres, "book-image.png"),
    new Book(1, "1983", "Orwell", "Fiction", "Anti-utopy", "21938432", new Publisher(1, "World Books"), "1953-10-05", 30.22, this.browsingGenres, "book-image.png"),
  ];

  private route = inject(ActivatedRoute);
  private router = inject(Router);
  query = '';

  formGroup: FormGroup = new FormGroup({
    search: new FormControl('')
  })

  selectedFilters = signal<Record<string, string[]>>({});

  effect = effect(() => {
    console.log(this.selectedFilters());
  });

  ngOnInit(): void {
    this.route.queryParamMap.subscribe(params => {
      this.query = params.get('query') ?? '';

      this.formGroup.patchValue({ search: this.query }, { emitEvent: false });

      const filters: Record<string, string[]> = {};

      const genres = params.getAll('genre') ?? [];
      if (genres.length) filters['genre'] = genres;

      // if you also use 'author' param(s), handle similarly:
      const authors = params.getAll('author') ?? [];
      if (authors.length) filters['author'] = authors;

      // single-value keys (e.g. category) can be mapped too:
      const category = params.get('category');
      if (category) filters['category'] = [category];
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

    // merge with existing query params (and remove empty ones)
    this.router.navigate([], {
      relativeTo: this.route,
      queryParams: qp,
      queryParamsHandling: 'merge'
    });
  }
}
