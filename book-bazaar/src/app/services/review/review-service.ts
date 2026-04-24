import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { PageResponse } from '../../model/pageResponse';
import { Review } from '../../model/review';
import { ReviewMetrics } from '../../model/review-metric';
import { ReviewRequest } from '../../model/review-request';

@Injectable({
  providedIn: 'root'
})
export class ReviewService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:9000/review-service/api'; 

  getReviews(
    bookId: number, 
    page: number = 0, 
    size: number = 10, 
    sort: string = 'createdAt,desc',
    rating?: number
  ): Observable<PageResponse<Review>> {
    
    const criteria = [`bookId=${bookId}`];
    
    if (rating) {
      criteria.push(`rating=${rating}`);
    }

    let params = new HttpParams()
      .set('pageIndex', page)
      .set('pageSize', size)
      .set('sort', sort)
      .set('search', criteria.join(','));

    return this.http.get<PageResponse<Review>>(`${this.apiUrl}/reviews`, { params });
  }

  getBookMetrics(bookId: number): Observable<ReviewMetrics> {
    return this.http.get<ReviewMetrics>(`${this.apiUrl}/review-metrics/by-book/${bookId}`);
  }

  createReview(request: ReviewRequest): Observable<Review> {
    return this.http.post<Review>(`${this.apiUrl}/reviews`, request);
  }

  updateReview(id: string, request: ReviewRequest): Observable<Review> {
    return this.http.put<Review>(`${this.apiUrl}/reviews/${id}`, request);
  }

  getUserReview(bookId: number, userId: string): Observable<Review | null> {
    const params = new HttpParams()
      .set('pageIndex', 0)
      .set('pageSize', 1)
      .set('search', `bookId=${bookId},userId=${userId}`);

    return this.http.get<PageResponse<Review>>(`${this.apiUrl}/reviews`, { params }).pipe(
      map(page => page.items.length > 0 ? page.items[0] : null)
    );
  }

  getReviewsByUserId(
    userId: string, 
    page: number = 0, 
    size: number = 10, 
    sort: string = 'createdAt,desc'
  ): Observable<PageResponse<Review>> {
    
    const search = `userId=${userId}`;

    let params = new HttpParams()
      .set('pageIndex', page)
      .set('pageSize', size)
      .set('sort', sort)
      .set('search', search);

    return this.http.get<PageResponse<Review>>(`${this.apiUrl}/reviews`, { params });
  }

  getTopRelevantReviews(size: number = 6): Observable<PageResponse<Review>> {
    const params = new HttpParams()
      .set('pageIndex', 0)
      .set('pageSize', size)
      .set('sort', 'scoringResult.score,desc');
    return this.http.get<PageResponse<Review>>(`${this.apiUrl}/reviews`, { params });
  }

  deleteReview(reviewId: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/reviews/${reviewId}`);
  }
}