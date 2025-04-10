import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MaterialModule } from '../common/material.module';
import { ReactiveFormsModule, FormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';

@Component({
  selector: 'app-report-bug-dialog',
  standalone: true,
  imports: [MaterialModule, ReactiveFormsModule, FormsModule],
  templateUrl: './report-bug-dialog.component.html',
  styleUrl: './report-bug-dialog.component.css'
})
export class ReportBugDialogComponent {
  bugForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<ReportBugDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.bugForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      description: ['', [Validators.required, Validators.minLength(5)]]
    });
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  onReport(): void {
    if (this.bugForm.valid) {
      this.dialogRef.close(this.bugForm.value);
    }
  }
}
