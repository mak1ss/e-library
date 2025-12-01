import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PageResponse } from '../../model/pageResponse';
import { Review } from '../../model/review';
import { ReviewMetrics } from '../../model/review-metric';

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
}