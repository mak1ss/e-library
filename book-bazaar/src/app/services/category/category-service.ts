import { inject, Injectable } from '@angular/core';
import { Category } from '../../model/category';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PageResponse } from '../../model/pageResponse';

@Injectable({
  providedIn: 'root',
})
export class CategoryService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:9000/book-service/api/categories';

  getCategories(page: number = 0, size: number = 10): Observable<PageResponse<Category>> {
    let params = new HttpParams()
      .set('pageIndex', page)
      .set('pageSize', size);

    return this.http.get<PageResponse<Category>>(this.apiUrl, { params });
  }
}
