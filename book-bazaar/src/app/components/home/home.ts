import {Component, inject} from '@angular/core';
import {MatFormField} from '@angular/material/input';
import {MatInput} from '@angular/material/input';
import {FormControl, FormGroup, ReactiveFormsModule} from '@angular/forms';
import {Router, RouterLink} from '@angular/router';
import {Genre} from '../../model/genre';
import {MatRipple} from '@angular/material/core';
import {MatButton} from '@angular/material/button';
import {Book} from '../../model/book';
import {Publisher} from '../../model/publisher';
import {MatCard, MatCardSubtitle, MatCardTitle, MatCardTitleGroup, MatCardXlImage} from '@angular/material/card';
import {MatChip, MatChipSet} from '@angular/material/chips';

@Component({
  selector: 'app-home',
  imports: [
    MatFormField,
    MatInput,
    ReactiveFormsModule,
    MatRipple,
    MatButton,
    MatCard,
    MatCardTitle,
    MatCardTitleGroup,
    MatCardSubtitle,
    MatCardXlImage,
    RouterLink,
    MatChipSet,
    MatChip,
  ],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home {
  protected router = inject(Router);

  protected formGroup: FormGroup = new FormGroup(
    {
      search: new FormControl('')
    }
  );

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

  protected search() {
    let filter = this.formGroup.value.search;
    if (!filter) return;

    this.router.navigate(['/search'], {queryParams: {query: filter}});
  }

  protected searchByGenre(genre: Genre) {
    this.router.navigate(['/search'], {queryParams: {genre: genre.name}});
  }
}
