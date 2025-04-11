import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MaterialModule } from '../common/material.module';
import { ReactiveFormsModule, FormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ChatCommunicationService } from '../services/chat_service';
import { ChatService } from '../services/chatbot.services';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-report-bug-dialog',
  standalone: true,
  imports: [MaterialModule, ReactiveFormsModule, FormsModule],
  templateUrl: './report-bug-dialog.component.html',
  styleUrls: ['./report-bug-dialog.component.css']
})
export class ReportBugDialogComponent {
  bugForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<ReportBugDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any,
    private bugReportService: ChatService,
    private snackBar: MatSnackBar
  ) {
    this.bugForm = this.fb.group({
      // email: ['', [Validators.required, Validators.email]],
      description: ['', [Validators.required, Validators.minLength(5)]]
    });
  }

  onCancel(): void {
    this.dialogRef.close();
  }

  onReport(): void {
    if (this.bugForm.valid) {
      const bugData = this.bugForm.value;
      this.bugReportService.reportBug(bugData).subscribe(
        (response) => {
          this.snackBar.open('Bug report sent successfully!', 'Close', {
            duration: 3000,
            panelClass: ['snackbar-success']
          });
          this.dialogRef.close();
        },
        (error) => {
          this.snackBar.open('Bug report sent successfully!', 'Close', {
            duration: 3000,
            panelClass: ['snackbar-success']
          });
          this.dialogRef.close();
        }
      );
    }
  }
}
