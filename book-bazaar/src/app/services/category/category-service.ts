import { inject, Injectable } from '@angular/core';
import { Category } from '../../model/category';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PageResponse } from '../../model/pageResponse';

export interface CategoryRequest {
  name: string;
  description: string;
}

@Injectable({
  providedIn: 'root',
})
export class CategoryService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:9000/book-service/api/categories';

  getCategories(page: number = 0, size: number = 10, search?: string): Observable<PageResponse<Category>> {
    let params = new HttpParams()
      .set('pageIndex', page)
      .set('pageSize', size);

    if (search) {
      params = params.set('search', `name:${search}`);
    }

    return this.http.get<PageResponse<Category>>(this.apiUrl, { params });
  }

  createCategory(request: CategoryRequest): Observable<Category> {
    return this.http.post<Category>(this.apiUrl, request);
  }

  updateCategory(id: number, request: CategoryRequest): Observable<Category> {
    return this.http.put<Category>(`${this.apiUrl}/${id}`, request);
  }

  deleteCategory(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
