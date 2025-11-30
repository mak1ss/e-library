import { inject, Injectable } from '@angular/core';
import { Genre } from '../../model/genre';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PageResponse } from '../../model/pageResponse';

@Injectable({
  providedIn: 'root',
})
export class GenreService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:9000/book-service/api/genres';

  getGenres(page: number = 0, size: number = 10): Observable<PageResponse<Genre>> {
    let params = new HttpParams()
      .set('pageIndex', page)
      .set('pageSize', size);

    return this.http.get<PageResponse<Genre>>(this.apiUrl, { params });
  }
}
