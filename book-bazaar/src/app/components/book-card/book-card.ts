import { Component, input } from '@angular/core';
import { Book } from '../../model/book';
import { MatCard, MatCardTitleGroup, MatCardTitle, MatCardSubtitle } from "@angular/material/card";
import { RouterModule } from '@angular/router';
import { MatChipSet, MatChip } from "@angular/material/chips";

@Component({
  selector: 'app-book-card',
  imports: [MatCard, RouterModule, MatCardTitleGroup, MatCardTitle, MatCardSubtitle, MatChipSet, MatChip],
  templateUrl: './book-card.html',
  styleUrl: './book-card.css',
})
export class BookCard {
    book = input.required<Book>();
}
