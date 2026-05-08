import { inject, Injectable } from '@angular/core';
import { Publisher } from '../../model/publisher';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PageResponse } from '../../model/pageResponse';

export interface PublisherRequest {
  name: string;
  address: string;
}

@Injectable({
  providedIn: 'root',
})
export class PublisherService {
  private http = inject(HttpClient);
  private apiUrl = 'http://localhost:9000/book-service/api/publishers';

  getPublishers(page: number = 0, size: number = 10, search?: string): Observable<PageResponse<Publisher>> {
    let params = new HttpParams()
      .set('pageIndex', page)
      .set('pageSize', size);

    if (search) {
      params = params.set('search', `name:${search}`);
    }

    return this.http.get<PageResponse<Publisher>>(this.apiUrl, { params });
  }

  createPublisher(request: PublisherRequest): Observable<Publisher> {
    return this.http.post<Publisher>(this.apiUrl, request);
  }

  updatePublisher(id: number, request: PublisherRequest): Observable<Publisher> {
    return this.http.put<Publisher>(`${this.apiUrl}/${id}`, request);
  }

  deletePublisher(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
