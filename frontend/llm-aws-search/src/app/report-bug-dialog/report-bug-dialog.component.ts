import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { MaterialModule } from '../common/material.module';
import { ReactiveFormsModule, FormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ChatCommunicationService } from '../services/chat_service';
import { ChatService } from '../services/chatbot.services';

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
    private bugReportService: ChatService
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
    console.log("USAOO 35")
    if (this.bugForm.valid) {
      console.log("USAOO")
      const bugData = this.bugForm.value;
      this.bugReportService.reportBug(bugData).subscribe(
        (response) => {
          console.log('Bug report sent successfully:', response);
          this.dialogRef.close();
        },
        (error) => {
          console.error('Error sending bug report:', error);
        }
      );
    }
  }
}
