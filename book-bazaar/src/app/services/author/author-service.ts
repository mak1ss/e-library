import { inject, Injectable } from '@angular/core';
import { Author } from '../../model/author';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PageResponse } from '../../model/pageResponse';

export interface AuthorRequest {
  name: string;
  bio?: string;
}

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

  createAuthor(request: AuthorRequest): Observable<Author> {
    return this.http.post<Author>(this.apiUrl, request);
  }

  updateAuthor(id: number, request: AuthorRequest): Observable<Author> {
    return this.http.put<Author>(`${this.apiUrl}/${id}`, request);
  }

  deleteAuthor(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
