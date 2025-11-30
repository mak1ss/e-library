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
  getBooks(filters: Record<string, any> = {}, page: number = 0, size: number = 10): Observable<PageResponse<Book>> {
    let params = new HttpParams()
      .set('pageIndex', page)
      .set('pageSize', size);

    // Проходимося по всіх фільтрах і додаємо їх у параметри запиту
    Object.entries(filters).forEach(([key, value]) => {
      if (value) {
        if (Array.isArray(value)) {
          // Якщо це масив (наприклад, декілька жанрів), додаємо кожен окремо
          value.forEach(item => {
            params = params.append(key, item);
          });
        } else {
          params = params.set(key, value);
        }
      }
    });

    return this.http.get<PageResponse<Book>>(this.baseUrl, { params });
  }
  
  // Метод для отримання однієї книги (деталі)
  getBookById(id: number): Observable<Book> {
    return this.http.get<Book>(`${this.baseUrl}/${id}`);
  }
}
