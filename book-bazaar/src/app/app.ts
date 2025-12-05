import { Component, inject, signal } from '@angular/core';
import { NavigationEnd, Router, RouterOutlet, Scroll } from '@angular/router';
import {Header} from './components/header/header';
import {Footer} from './components/footer/footer';
import { ViewportScroller } from '@angular/common';
import { filter } from 'rxjs';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, Header, Footer],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  private router = inject(Router);
  private viewportScroller = inject(ViewportScroller);
  
  private currentPath = '';

  constructor() {
    this.router.events.pipe(
      filter((e): e is Scroll => e instanceof Scroll)
    ).subscribe(e => {
      
      if (e.position) {
        this.viewportScroller.scrollToPosition(e.position);
      } else if (e.anchor) {
        this.viewportScroller.scrollToAnchor(e.anchor);
      } else {
        const url = (e.routerEvent instanceof NavigationEnd) 
          ? e.routerEvent.urlAfterRedirects 
          : e.routerEvent.url;

        const newPath = this.stripParams(url);

        // Скролимо нагору ТІЛЬКИ якщо змінився шлях (наприклад Home -> Search)
        // Якщо шлях той самий (/search -> /search?genre=Fantasy), скрол не чіпаємо
        if (newPath !== this.currentPath) {
          this.viewportScroller.scrollToPosition([0, 0]);
        }
        
        this.currentPath = newPath;
      }
    });
  }

  private stripParams(url: string): string {
    return url.split('?')[0];
  }
}
