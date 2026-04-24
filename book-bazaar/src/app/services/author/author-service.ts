import { inject, Injectable } from '@angular/core';
import { Author } from '../../model/author';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PageResponse } from '../../model/pageResponse';

@Injectable({
  providedIn: 'root',
})
export class AuthorService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:9000/book-service/api/authors';

  getAuthors(page: number = 0, size: number = 12, search?: string, sort: string = 'name,asc'): Observable<PageResponse<Author>> {
    let params = new HttpParams()
      .set('pageIndex', page)
      .set('pageSize', size)
      .set('sort', sort);

    if (search) {
      params = params.set('search', `name:${search}`);
    }

    return this.http.get<PageResponse<Author>>(this.apiUrl, { params });
  }

  getAuthorById(id: number): Observable<Author> {
    return this.http.get<Author>(`${this.apiUrl}/${id}`);
  }
}
