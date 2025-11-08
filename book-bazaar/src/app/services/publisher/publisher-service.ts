import { Injectable } from '@angular/core';
import { Publisher } from '../../model/publisher';

@Injectable({
  providedIn: 'root',
})
export class PublisherService {
  publishers: Publisher[] = [
    new Publisher(1, "Penguin Random House"),
    new Publisher(2, "HarperCollins"),
    new Publisher(3, "Simon & Schuster"),
    new Publisher(4, "Hachette Book Group"),
    new Publisher(5, "Macmillan Publishers"),
  ]

  getPublishers(): Publisher[] {
    return this.publishers;
  }
}
