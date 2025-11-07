import {Component, inject} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {MatFormField, MatInput} from '@angular/material/input';
import {FormControl, FormGroup, ReactiveFormsModule} from '@angular/forms';
import {MatButton} from '@angular/material/button';
import {FilterPanel} from '../filter-panel/filter-panel';
import {Book} from '../../model/book';
import {Publisher} from '../../model/publisher';
import {Genre} from '../../model/genre';

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
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  query = '';

  formGroup: FormGroup = new FormGroup({
    search: new FormControl('')
  })

  ngOnInit(): void {
    this.route.queryParamMap.subscribe(params => {
      this.query = params.get('query') ?? '';

      this.formGroup.patchValue({ search: this.query }, {emitEvent: false});
    })
  }

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

  protected search():void {
    this.query = this.formGroup.value.search ?? '';

    this.router.navigate([], {
      queryParams: {query: this.query},
      relativeTo: this.route,
      queryParamsHandling: 'merge'
    })
    console.log(this.query);
  }
}
