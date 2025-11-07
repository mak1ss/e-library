import { Component } from '@angular/core';
import {MatButton} from '@angular/material/button';
import {RouterLink} from '@angular/router';

@Component({
  selector: 'app-header',
  imports: [
    MatButton,
    RouterLink

  ],
  templateUrl: './header.html',
  styleUrl: './header.css',
})
export class Header {

}
