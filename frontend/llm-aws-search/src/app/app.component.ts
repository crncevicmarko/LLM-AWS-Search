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
userMessages:string [] = [];  // Array to store the chat messages
botMessages:string[]=[];
time:string=new Date().toLocaleTimeString();
constructor(private appService: AppService,private cdRef: ChangeDetectorRef) { }


  // Function to handle form submission
  onSubmit() {
    console.log(this.userInput);
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
    // Send the POST requestq
    this.appService.recieveUserInput(payload).subscribe(res=> { const parsedResponse = JSON.parse(res.body);
    console.log(parsedResponse);
    //console.log(payload);
      setTimeout(() => {
        this.botMessages.push(parsedResponse);
        this.thinking = false; // Enable button after delay
      }, 1000); // Adjust the delay as needed
    });
  }
  
  isSameAsLastPrompt(): boolean {
    console.log(this.userMessages[this.userMessages.length-1]);
    console.log(this.userInput);
    return this.userMessages[this.userMessages.length-1] === this.userInput;
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