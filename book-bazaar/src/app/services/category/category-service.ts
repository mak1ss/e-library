import { Injectable } from '@angular/core';
import { Category } from '../../model/category';

@Injectable({
  providedIn: 'root',
})
export class CategoryService {
  categories: Category[] = [
    new Category(1, "Fiction", "Fictional works including novels and short stories."),
    new Category(2, "Non-Fiction", "Informative and factual books."),
    new Category(3, "Science Fiction", "Books exploring futuristic concepts and advanced technology."),
    new Category(4, "Biography", "Life stories of notable individuals."),
    new Category(5, "Fantasy", "Books featuring magical and supernatural elements."),
  ];

  getCategories(): Category[] {
    return this.categories;
  }
}
