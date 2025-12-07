import { inject, Injectable } from '@angular/core';
import { Book } from '../../model/book';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PageResponse } from '../../model/pageResponse';

@Injectable({
  providedIn: 'root',
})
export class BookService {

  private baseUrl = 'http://localhost:9000/book-service/api/books';
  private http: HttpClient = inject(HttpClient);

  /**
   * Отримує список книг з фільтрацією та пагінацією
   * @param filters - об'єкт з фільтрами (наприклад, { genre: ['Fantasy'], query: 'Harry' })
   * @param page - номер сторінки (починаючи з 0)
   * @param size - розмір сторінки
   */
  getBooks(filters: Record<string, any> = {}, page: number = 0, size: number = 10, sort: string = 'title,asc'): Observable<PageResponse<Book>> {
    let params = new HttpParams()
      .set('pageIndex', page)
      .set('pageSize', size)
      .set('sort', sort);

    const searchCriteria: string[] = [];

    if (filters['query']) {
      searchCriteria.push(`title:${filters['query']}`);
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

    console.log('Generated Params:', params.toString()); // Для дебагу
    return this.http.get<PageResponse<Book>>(this.baseUrl, { params });
  }

  getBookById(id: number): Observable<Book> {
    return this.http.get<Book>(`${this.baseUrl}/${id}`);
  }
}
