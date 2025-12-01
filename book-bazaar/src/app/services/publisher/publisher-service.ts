import { inject, Injectable } from '@angular/core';
import { Publisher } from '../../model/publisher';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PageResponse } from '../../model/pageResponse';

@Injectable({
  providedIn: 'root',
})
export class PublisherService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:9000/book-service/api/publishers';

  getPublishers(page: number = 0, size: number = 10): Observable<PageResponse<Publisher>> {
    let params = new HttpParams()
      .set('pageIndex', page)
      .set('pageSize', size);
    return this.http.get<PageResponse<Publisher>>(this.apiUrl, { params });
  }
}
