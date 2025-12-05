import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UserReviewCard } from './user-review-card';

describe('UserReviewCard', () => {
  let component: UserReviewCard;
  let fixture: ComponentFixture<UserReviewCard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UserReviewCard]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UserReviewCard);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
