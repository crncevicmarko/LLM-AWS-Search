import { AfterViewChecked, Component,ElementRef,OnInit,ViewChild } from '@angular/core';
import { ChatService } from '../services/chatbot.services';
import { ChangeDetectorRef } from '@angular/core';
import { MarkdownDisplayComponent } from '../markdown-display/markdown-display.component';
import { ActivatedRoute, Router } from '@angular/router';
import { Chat } from '../models/chat.model';
import { ChatCommunicationService } from '../services/chat_service';
import { AuthService } from '../services/auth.service';
import { MatDialog } from '@angular/material/dialog';
import { ReportBugDialogComponent } from '../report-bug-dialog/report-bug-dialog.component';


@Component({
  selector: 'app-chatbot',
  templateUrl: './chatbot.component.html',
  styleUrl: './chatbot.component.css',
  standalone:false,
})

export class ChatbotComponent implements OnInit{
  isLoggedIn: boolean = false;

  title = 'llm-aws-search';
thinking: boolean=false;
@ViewChild('chatBox') chatBox: ElementRef | undefined;
@ViewChild('chatInput') chatInput: ElementRef | undefined;
userInput: string = ''; // Variable to bind input value
userMessages:string [] = [];  // Array to store the chat messages
botMessages:string[]=[];
time:string=new Date().toLocaleTimeString();
htmlContent:string="";
typingSpeed: number = 50;
chatId: string = '';
chat: any;
user_id : any;
constructor(
  private chatService: ChatService,
  private chatCommunicationService: ChatCommunicationService,
  private cdRef: ChangeDetectorRef,
  private mdComp:MarkdownDisplayComponent,
  private route: ActivatedRoute,
  private authService: AuthService,
  private router: Router,
  private dialog: MatDialog
) { }

  ngOnInit(): void {
    const token = this.authService.getAccessTokenFromLocalStorage();
    this.user_id=this.authService.getUserID();
    if (token) this.isLoggedIn = true;
    else this.isLoggedIn = false;
    this.route.paramMap.subscribe(params => {
      this.chatId = params.get('id')!;
    });
    
  }

  onSubmit() {
    const uuid = crypto.randomUUID();
    const userMessage = this.userInput;

    // create new chat in sidebar component
    this.chatCommunicationService.sendUserInput(userMessage, uuid);
    this.chatCommunicationService.saveChat(this.user_id,userMessage,uuid).subscribe({
      next: (response: any) => {
        const parsedResponse = response?.response;
        console.log("ovo je response generate title:" + parsedResponse)
        this.chatCommunicationService.saveTitleLocally(this.user_id, uuid, parsedResponse);
        console.log("Title saved locally.");

        // Optionally refresh UI or notify user

        // If you really want a page refresh, you can emit the refresh event:
        // this.chatCommunicationService.refreshPage$.next(true);
      },
      error: (err:any) => {
        console.error("Error saving chat title:", err);
      }
    });
    this.router.navigate(['/chat', uuid]);
  }

  resizeInput(inputElement: HTMLTextAreaElement): void {

    inputElement.style.height = 'auto';

    inputElement.style.height = `${inputElement.scrollHeight}px`;

    if (inputElement.scrollHeight > 100) {
      inputElement.style.height = '100px';
    }
  }

  logOut(): void {
    this.authService.signOut();
    this.router.navigate(['login']);
  }

  reportBug() {
    const dialogRef = this.dialog.open(ReportBugDialogComponent, {
      width: '500px',
      data: {}
    });

    dialogRef.afterClosed().subscribe(result => {
      if (result) {
        console.log('Bug reported:', result);
      }
    });
  }
}

