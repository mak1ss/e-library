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

  getAuthors(page: number = 0, size: number = 10): Observable<PageResponse<Author>> {
    let params = new HttpParams()
      .set('pageIndex', page)
      .set('pageSize', size);

    return this.http.get<PageResponse<Author>>(this.apiUrl, { params });
  }
}
