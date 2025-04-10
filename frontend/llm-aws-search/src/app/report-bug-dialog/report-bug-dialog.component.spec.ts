import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReportBugDialogComponent } from './report-bug-dialog.component';

describe('ReportBugDialogComponent', () => {
  let component: ReportBugDialogComponent;
  let fixture: ComponentFixture<ReportBugDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReportBugDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ReportBugDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
