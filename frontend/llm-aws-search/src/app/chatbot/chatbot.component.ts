import { AfterViewChecked, Component,ElementRef,ViewChild } from '@angular/core';
import { AppService } from '../services/app.services';
import { ChangeDetectorRef } from '@angular/core';
import { MarkdownDisplayComponent } from '../markdown-display/markdown-display.component';


@Component({
  selector: 'app-chatbot',
  templateUrl: './chatbot.component.html',
  styleUrl: './chatbot.component.css',
  standalone:false,
})
export class ChatbotComponent {
  

  title = 'llm-aws-search';
thinking: boolean=false;
@ViewChild('chatBox') chatBox: ElementRef | undefined;
@ViewChild('chatInput') chatInput: ElementRef | undefined;
userInput: string = ''; // Variable to bind input value
userMessages:string [] = [];  // Array to store the chat messages
botMessages:string[]=[];
time:string=new Date().toLocaleTimeString();
htmlContent:string="";
constructor(private appService: AppService,private cdRef: ChangeDetectorRef,private mdComp:MarkdownDisplayComponent) { }

  // Function to handle form submission
  onSubmit() {
    if (this.isSameAsLastPrompt())
    {
      alert('Your input is the same as the last prompt. Please enter something different.');
      return
    }
    // Prepare the data payload
    const payload = { message: this.userInput };
    this.userMessages.push(this.userInput);
    this.thinking=true;
    this.userInput="";
    // Send the POST request

    this.appService.recieveUserInput(payload).subscribe(res=> { const parsedResponse = res.response[0];
      setTimeout(() => {
        console.log(parsedResponse)
        const ticketUrl = (parsedResponse && parsedResponse['ticket-url']) || '';
        const ticketText=(parsedResponse && parsedResponse.text || '');
        this.botMessages.push(ticketText+"\n LINK TO TICKET:"+this.mdComp.convertMarkdownToHTML(ticketUrl));
        this.thinking = false; // Enable button after delay
      }, 1000); // Adjust the delay as needed
    });
  }
  

  isSameAsLastPrompt(): boolean {

    return this.userMessages[this.userMessages.length-1] === this.userInput;
  }
  
  ngAfterViewChecked(): void {
    this.autoScroll();
  }
  resizeInput(inputElement: HTMLTextAreaElement): void {
    // Reset the height of the input element
    
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
}
