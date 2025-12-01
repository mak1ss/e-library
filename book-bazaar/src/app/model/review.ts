export interface Review {
  id: string;
  userId: string;
  firstName?: string;
  lastName?: string;
  avatarUrl?: string;
  bookId: number;
  createdAt: string;
  rating: number;
  text: string;
}