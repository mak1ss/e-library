import { inject, Injectable } from '@angular/core';
import { Book } from '../../model/book';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PageResponse } from '../../model/pageResponse';

export interface BookRequest {
  title: string;
  authorId: number;
  categoryId: number;
  genreIdList: number[];
  description?: string;
  ISBN?: string;
  publisherId: number;
  releaseDate?: string;
  price: number;
}

@Injectable({
  providedIn: 'root',
})
export class BookService {

  private baseUrl = 'http://localhost:9000/book-service/api/books';
  private http: HttpClient = inject(HttpClient);

  getBooks(filters: Record<string, any> = {}, page: number = 0, size: number = 10, sort: string = 'title,asc'): Observable<PageResponse<Book>> {
    let params = new HttpParams()
      .set('pageIndex', page)
      .set('pageSize', size)
      .set('sort', sort);

    const searchCriteria: string[] = [];

    if (filters['query']) {
      searchCriteria.push(`q:${filters['query']}`);
    }

    if (filters['genre'] && filters['genre'].length > 0) {
      const genresStr = Array.isArray(filters['genre'])
        ? filters['genre'].join('||')
        : filters['genre'];
      searchCriteria.push(`genres_=${genresStr}`);
    }

    if (filters['author'] && filters['author'].length > 0) {
      const authorsStr = Array.isArray(filters['author'])
        ? filters['author'].join('||')
        : filters['author'];
      searchCriteria.push(`author_=${authorsStr}`);
    }

    if (filters['category'] && filters['category'].length > 0) {
      const catStr = Array.isArray(filters['category'])
        ? filters['category'].join('||')
        : filters['category'];
      searchCriteria.push(`category_=${catStr}`);
    }

    if (filters['publisher'] && filters['publisher'].length > 0) {
      const pubStr = Array.isArray(filters['publisher'])
        ? filters['publisher'].join('||')
        : filters['publisher'];
      searchCriteria.push(`publisher_=${pubStr}`);
    }

    if (filters['minPrice'] !== null && filters['minPrice'] !== undefined) {
      searchCriteria.push(`price>=${filters['minPrice']}`);
    }
    if (filters['maxPrice'] !== null && filters['maxPrice'] !== undefined) {
      searchCriteria.push(`price<=${filters['maxPrice']}`);
    }

    if (filters['minRating'] !== null && filters['minRating'] !== undefined) {
      searchCriteria.push(`averageRating>=${filters['minRating']}`);
    }
    if (filters['maxRating'] !== null && filters['maxRating'] !== undefined) {
      searchCriteria.push(`averageRating<=${filters['maxRating']}`);
    }

    if (searchCriteria.length > 0) {
      params = params.set('search', searchCriteria.join(','));
    }

    return this.http.get<PageResponse<Book>>(this.baseUrl, { params });
  }

  getBookById(id: number): Observable<Book> {
    return this.http.get<Book>(`${this.baseUrl}/${id}`);
  }

  getSimilarBooks(bookId: number, topK: number = 10): Observable<PageResponse<Book>> {
    const params = new HttpParams().set('topK', topK.toString());
    return this.http.get<PageResponse<Book>>(`${this.baseUrl}/${bookId}/similar`, { params });
  }

  getPersonalizedRecommendations(topK: number = 10): Observable<PageResponse<Book>> {
    const params = new HttpParams().set('topK', topK.toString());
    return this.http.get<PageResponse<Book>>(`${this.baseUrl}/recommendations/personal`, { params });
  }

  createBook(request: BookRequest): Observable<Book> {
    return this.http.post<Book>(this.baseUrl, request);
  }

  updateBook(id: number, request: BookRequest): Observable<Book> {
    return this.http.put<Book>(`${this.baseUrl}/${id}`, request);
  }

  deleteBook(id: number): Observable<void> {
    return this.http.delete<void>(`${this.baseUrl}/${id}`);
  }

  uploadCover(bookId: number, file: File): Observable<Book> {
    const formData = new FormData();
    formData.append('file', file);
    return this.http.post<Book>(`${this.baseUrl}/${bookId}/cover`, formData);
  }
}
