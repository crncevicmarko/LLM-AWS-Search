import { AfterViewChecked, Component,ElementRef,ViewChild } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AppService } from './services/app.services';
import { ChangeDetectorRef } from '@angular/core';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
  standalone:false,
  
})
export class AppComponent implements AfterViewChecked{
  title = 'llm-aws-search';
thinking: boolean=false;
@ViewChild('chatBox') chatBox: ElementRef | undefined;
@ViewChild('chatInput') chatInput: ElementRef | undefined;
userInput: string = ''; // Variable to bind input value
messages:string [] = [];  // Array to store the chat messages
time:string=new Date().toLocaleTimeString();
constructor(private appService: AppService,private cdRef: ChangeDetectorRef) { }


  // Function to handle form submission
  onSubmit() {

    // Prepare the data payload
    const payload = { message: this.userInput };
    this.messages.push("You: "+this.userInput);
    this.thinking=true;
    this.userInput="";
    // Send the POST requestq
    this.appService.recieveUserInput(payload).subscribe(res=> { const parsedResponse = JSON.parse(res.body);
    console.log(parsedResponse);
    const botResponse = "ChatBot: " + parsedResponse.message;
    //console.log(payload);
      setTimeout(() => {
        this.messages.push(botResponse);
        this.thinking = false; // Enable button after delay
      }, 1000); // Adjust the delay as needed
    });
  }
  
  ngAfterViewChecked(): void {
    this.autoScroll();
  }
  resizeInput(inputElement: HTMLInputElement): void {
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