export interface ReviewRequest {
  bookId: number;
  rating: number;
  text?: string;
}