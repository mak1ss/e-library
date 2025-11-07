import { Routes } from '@angular/router';
import {Home} from './components/home/home';
import {SearchBooks} from './components/search-books/search-books';
import {BookDetails} from './components/book-details/book-details';

export const routes: Routes = [
  {
    path: '', component: Home
  },
  {
    path: "search", component: SearchBooks
  },
  {
    path: "book-details/:bookId", component: BookDetails
  }
];
