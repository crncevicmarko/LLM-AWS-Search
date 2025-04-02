import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MarkdownDisplayComponent } from './markdown-display.component';

describe('MarkdownDisplayComponent', () => {
  let component: MarkdownDisplayComponent;
  let fixture: ComponentFixture<MarkdownDisplayComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MarkdownDisplayComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MarkdownDisplayComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
