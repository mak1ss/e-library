export interface ReviewMetrics {
  id: string;
  bookId: number;
  totalReviews: number;
  averageRating: number;
  reviewCountsRating: Record<string, number>; 
}