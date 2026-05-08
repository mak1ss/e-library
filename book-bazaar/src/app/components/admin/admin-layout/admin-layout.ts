import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-admin-layout',
  standalone: true,
  imports: [RouterModule, MatIconModule],
  templateUrl: './admin-layout.html',
})
export class AdminLayout {}
