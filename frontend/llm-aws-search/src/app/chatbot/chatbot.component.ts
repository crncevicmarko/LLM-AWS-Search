import { AfterViewChecked, Component,ElementRef,OnInit,ViewChild } from '@angular/core';
import { ChatService } from '../services/chatbot.services';
import { ChangeDetectorRef } from '@angular/core';
import { MarkdownDisplayComponent } from '../markdown-display/markdown-display.component';
import { ActivatedRoute, Router } from '@angular/router';
import { Chat } from '../models/chat.model';
import { ChatCommunicationService } from '../services/chat_service';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';


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
constructor(
  private chatService: ChatService,
  private chatCommunicationService: ChatCommunicationService,
  private cdRef: ChangeDetectorRef,
  private mdComp:MarkdownDisplayComponent,
  private route: ActivatedRoute,
  private authService: AuthService,
  private router: Router
) { }

  ngOnInit(): void {
    const token = this.authService.getAccessTokenFromLocalStorage();
    if (token) this.isLoggedIn = true;
    else this.isLoggedIn = false;
    this.route.paramMap.subscribe(params => {
      this.chatId = params.get('id')!;
    });
  }

  onSubmit() {
    const uuid = crypto.randomUUID();
    console.log("Usli u onSubmit")
    const userMessage = this.userInput;
    console.log("User input: ", userMessage)
    // Create the chat
    const newChat = this.chatCommunicationService.startNewChat(1, uuid);
    console.log("New Chat: ", newChat)
  
    this.chatCommunicationService.sendUserInput(userMessage, uuid);
    this.router.navigate(['/chat', uuid]);
  }

  simulateTyping(response: string, responseIndex: number) {
    let words = response.split(' ');
    let currentWords = [];
    let index = 0;
    const wordsPerBatch = 5;
    const typingSpeed = 300;
    
    const intervalId = setInterval(() => {
      currentWords.push(...words.slice(index, index + wordsPerBatch));
      this.botMessages[responseIndex] = currentWords.join(" ");
      
      this.cdRef.detectChanges();

      index += wordsPerBatch;

      if (index >= words.length) {
        clearInterval(intervalId); 
        this.thinking = false;
      }
    }, typingSpeed);
  }

  isSameAsLastPrompt(): boolean {

    return this.userMessages[this.userMessages.length-1] === this.userInput;
  }
  
  ngAfterViewChecked(): void {
    this.autoScroll();
  }
  resizeInput(inputElement: HTMLTextAreaElement): void {
    
    inputElement.style.height = 'auto';

    inputElement.style.height = `${inputElement.scrollHeight}px`;

    if (inputElement.scrollHeight > 100) {
      inputElement.style.height = '100px';
    }
  }
  private autoScroll(): void {
    const chatBoxElement = this.chatBox?.nativeElement;
    if (chatBoxElement) {
      chatBoxElement.scrollTop = chatBoxElement.scrollHeight;
    }
  }

  logOut(): void {
    this.authService.signOut();
    this.router.navigate(['login']);
  }
}

