import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';

interface ResourceTile {
  label: string;
  icon: string;
  route: string;
  description: string;
}

@Component({
  selector: 'app-admin-dashboard',
  standalone: true,
  imports: [RouterModule, MatIconModule],
  templateUrl: './admin-dashboard.html',
})
export class AdminDashboard {
  readonly tiles: ResourceTile[] = [
    { label: 'Books', icon: 'menu_book', route: '/admin/books', description: 'Create, edit and remove books' },
    { label: 'Authors', icon: 'person', route: '/admin/authors', description: 'Manage author profiles' },
    { label: 'Categories', icon: 'category', route: '/admin/categories', description: 'Organise book categories' },
    { label: 'Genres', icon: 'label', route: '/admin/genres', description: 'Manage genres and tags' },
    { label: 'Publishers', icon: 'business', route: '/admin/publishers', description: 'Manage publishing houses' },
  ];
}
