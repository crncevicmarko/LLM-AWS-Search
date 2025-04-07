import { AfterViewChecked, Component,ElementRef,ViewChild } from '@angular/core';
import { ChatService } from '../services/chatbot.services';
import { ChangeDetectorRef } from '@angular/core';
import { MarkdownDisplayComponent } from '../markdown-display/markdown-display.component';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';


@Component({
  selector: 'app-chatbot',
  templateUrl: './chatbot.component.html',
  styleUrl: './chatbot.component.css',
  standalone:false,
})
export class ChatbotComponent {
  isLoggedIn: boolean = false;
  
  title = 'llm-aws-search';
  thinking: boolean=false;
  @ViewChild('chatBox') chatBox: ElementRef | undefined;
  @ViewChild('chatInput') chatInput: ElementRef | undefined;
  userInput: string = ''; 
  userMessages:string [] = [];  
  botMessages:string[]=[];
  time:string=new Date().toLocaleTimeString();
  htmlContent:string="";
  typingSpeed: number = 50;

  constructor(private chatService: ChatService, 
    private cdRef: ChangeDetectorRef,
    private mdComp:MarkdownDisplayComponent,
    private authService: AuthService,
    private router: Router) { }

  ngOnInit() {
    const token = this.authService.getAccessTokenFromLocalStorage();
    if (token) this.isLoggedIn = true;
    else this.isLoggedIn = false;
  }

  onSubmit() {
    if (this.isSameAsLastPrompt())
    {
      alert('Your input is the same as the last prompt. Please enter something different.');
      return
    }
    const payload = { message: this.userInput };
    this.userMessages.push(this.userInput);
    this.thinking=true;
    this.userInput="";

    // this.chatService.recieveUserInput(payload).subscribe(res=> { const parsedResponse = res.response;
    //   setTimeout(() => {
    //     console.log(res);
    //     this.botMessages.push(this.mdComp.convertMarkdownToHTML(parsedResponse));
    //     this.thinking = false; // Enable button after delay
    //   }, 1000); // Adjust the delay as needed
    // });
    this.chatService.recieveUserInput(payload).subscribe(res => {
      const parsedResponse = this.mdComp.convertMarkdownToHTML(res.response);
  
      // Initialize empty message for typing effect
      this.botMessages.push("");
      const responseIndex = this.botMessages.length - 1;
  
      // Add a slight delay before starting to type
      // setTimeout(() => {
        this.simulateTyping(parsedResponse, responseIndex);
      // }, 200);
    });
  }

  simulateTyping(response: string, responseIndex: number) {
    let words = response.split(' ');
    let currentWords = [];
    let index = 0;
    const wordsPerBatch = 5; // Define the number of words per batch
    const typingSpeed = 300;  // Adjust typing speed for each batch of words
    
    const intervalId = setInterval(() => {
      currentWords.push(...words.slice(index, index + wordsPerBatch));
      this.botMessages[responseIndex] = currentWords.join(" "); // Join the words and update the message
      
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

    // Set the height to match the scrollHeight (to simulate expansion)
    inputElement.style.height = `${inputElement.scrollHeight}px`;

    // Ensure the height doesn't grow indefinitely, e.g., setting max-height
    if (inputElement.scrollHeight > 100) {
      inputElement.style.height = '100px'; // Max height, can be adjusted
    }
  }
  private autoScroll(): void {
    const chatBoxElement = this.chatBox?.nativeElement;
    if (chatBoxElement) {
      chatBoxElement.scrollTop = chatBoxElement.scrollHeight;
    }
  }

  logOut(): void {
    console.log("USO");
    this.authService.signOut();
    this.router.navigate(['login']);
  }
}
