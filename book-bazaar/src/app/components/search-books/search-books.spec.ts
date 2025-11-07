import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SearchBooks } from './search-books';

describe('SearchBooks', () => {
  let component: SearchBooks;
  let fixture: ComponentFixture<SearchBooks>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SearchBooks]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SearchBooks);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
