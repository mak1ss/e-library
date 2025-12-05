import { Routes } from '@angular/router';
import { Home } from './components/home/home';
import { SearchBooks } from './components/search-books/search-books';
import { BookDetails } from './components/book-details/book-details';
import { ReviewForm } from './components/review-form/review-form';
import { MyReviews } from './components/my-reviews/my-reviews';

export const routes: Routes = [
  {
    path: '', component: Home
  },
  {
    path: "search", component: SearchBooks
  },
  {
    path: "book-details/:bookId", component: BookDetails
  },
  {
    path: "book-details/:bookId/review", component: ReviewForm
  },
  {
    path: "my-reviews", component: MyReviews
  }
];
