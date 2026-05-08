import { Routes } from '@angular/router';
import { Home } from './components/home/home';
import { SearchBooks } from './components/search-books/search-books';
import { BookDetails } from './components/book-details/book-details';
import { ReviewForm } from './components/review-form/review-form';
import { MyReviews } from './components/my-reviews/my-reviews';
import { AuthorsPage } from './components/authors/authors';
import { AuthorDetails } from './components/author-details/author-details';
import { RecommendationsPage } from './components/recommendations/recommendations';
import { adminGuard } from './guards/admin.guard';
import { AdminLayout } from './components/admin/admin-layout/admin-layout';
import { AdminDashboard } from './components/admin/admin-dashboard/admin-dashboard';
import { AdminBooksPage } from './components/admin/admin-books/admin-books';
import { AdminAuthorsPage } from './components/admin/admin-authors/admin-authors';
import { AdminCategoriesPage } from './components/admin/admin-categories/admin-categories';
import { AdminGenresPage } from './components/admin/admin-genres/admin-genres';
import { AdminPublishersPage } from './components/admin/admin-publishers/admin-publishers';

export const routes: Routes = [
  { path: '', component: Home },
  { path: 'search', component: SearchBooks },
  { path: 'authors', component: AuthorsPage },
  { path: 'authors/:authorId', component: AuthorDetails },
  { path: 'book-details/:bookId', component: BookDetails },
  { path: 'book-details/:bookId/review', component: ReviewForm },
  { path: 'my-reviews', component: MyReviews },
  { path: 'recommendations', component: RecommendationsPage },
  {
    path: 'admin',
    canActivate: [adminGuard],
    component: AdminLayout,
    children: [
      { path: '', component: AdminDashboard },
      { path: 'books', component: AdminBooksPage },
      { path: 'authors', component: AdminAuthorsPage },
      { path: 'categories', component: AdminCategoriesPage },
      { path: 'genres', component: AdminGenresPage },
      { path: 'publishers', component: AdminPublishersPage },
    ]
  }
];
