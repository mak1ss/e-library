import { Component } from '@angular/core';
import {RouterLink} from '@angular/router';
import {NgOptimizedImage} from '@angular/common';

@Component({
  selector: 'app-footer',
  imports: [
    RouterLink,
    NgOptimizedImage
  ],
  templateUrl: './footer.html',
  styleUrl: './footer.css',
})
export class Footer {

}
