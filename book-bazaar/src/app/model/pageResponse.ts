export interface PageResponse<T> {
  items: T[];      
  total: number;
  size: number;
  pageNumber: number;
}