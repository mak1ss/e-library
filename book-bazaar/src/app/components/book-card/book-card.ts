import { Component, inject, input } from '@angular/core';
import { Book } from '../../model/book';
import { MatCard, MatCardTitleGroup, MatCardTitle, MatCardSubtitle } from "@angular/material/card";
import { Router, RouterModule } from '@angular/router';
import { MatChipSet, MatChip } from "@angular/material/chips";
import { MatTooltipModule } from '@angular/material/tooltip';
import { Category } from '../../model/category';
import { Genre } from '../../model/genre';
import { CurrencyPipe } from '@angular/common';

@Component({
  selector: 'app-book-card',
  imports: [MatCard, RouterModule, MatCardTitleGroup, MatCardTitle, MatCardSubtitle, MatChipSet, MatChip, MatTooltipModule, CurrencyPipe],
  templateUrl: './book-card.html',
  styleUrl: './book-card.css',
})
export class BookCard {
  book = input.required<Book>();

  private router = inject(Router);

  searchByGenre(event: Event, genre: Genre) {
    event.stopPropagation(); // Зупиняємо спливання події, щоб не спрацював клік по картці
    event.preventDefault();  // Запобігаємо дефолтній поведінці посилання

    if (genre.name) {
      this.router.navigate(['/search'], { queryParams: { genre: genre.name } }).then(() => window.scroll({
        top: 450,
        left: 0,
        behavior: 'smooth'
      }));
    }
  }

  // Перехід на пошук по категорії
  searchByCategory(event: Event, category: Category) {
    event.stopPropagation();
    event.preventDefault();

    if (category.name) {
      this.router.navigate(['/search'], { queryParams: { category: category.name } }).then(() => window.scroll({
        top: 450,
        left: 0,
        behavior: 'smooth'
      }));
    }
  }
}
