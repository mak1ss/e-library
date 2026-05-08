import { Routes } from '@angular/router';
import { Home } from './components/home/home';
import { SearchBooks } from './components/search-books/search-books';
import { BookDetails } from './components/book-details/book-details';
import { ReviewForm } from './components/review-form/review-form';
import { MyReviews } from './components/my-reviews/my-reviews';
import { AuthorsPage } from './components/authors/authors';
import { AuthorDetails } from './components/author-details/author-details';
import { RecommendationsPage } from './components/recommendations/recommendations';

export const routes: Routes = [
  {
    path: '', component: Home
  },
  {
    path: "search", component: SearchBooks
  },
  {
    path: "authors", component: AuthorsPage
  },
  {
    path: "authors/:authorId", component: AuthorDetails
  },
  {
    path: "book-details/:bookId", component: BookDetails
  },
  {
    path: "book-details/:bookId/review", component: ReviewForm
  },
  {
    path: "my-reviews", component: MyReviews
  },
  {
    path: "recommendations", component: RecommendationsPage
  }
];
