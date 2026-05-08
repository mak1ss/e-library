import { inject, Injectable } from '@angular/core';
import { Genre } from '../../model/genre';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PageResponse } from '../../model/pageResponse';

export interface GenreRequest {
  name: string;
  description: string;
}

@Injectable({
  providedIn: 'root',
})
export class GenreService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:9000/book-service/api/genres';

  getGenres(page: number = 0, size: number = 10, search?: string): Observable<PageResponse<Genre>> {
    let params = new HttpParams()
      .set('pageIndex', page)
      .set('pageSize', size);

    if (search) {
      params = params.set('search', `name:${search}`);
    }

    return this.http.get<PageResponse<Genre>>(this.apiUrl, { params });
  }

  createGenre(request: GenreRequest): Observable<Genre> {
    return this.http.post<Genre>(this.apiUrl, request);
  }

  updateGenre(id: number, request: GenreRequest): Observable<Genre> {
    return this.http.put<Genre>(`${this.apiUrl}/${id}`, request);
  }

  deleteGenre(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
