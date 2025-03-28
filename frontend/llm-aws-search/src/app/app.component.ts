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
userInput: string = ''; // Variable to bind input value
result:string='';
messages:string [] = [];  // Array to store the chat messages
time:string=new Date().toLocaleTimeString();
constructor(private appService: AppService,private cdRef: ChangeDetectorRef) { }


  // Function to handle form submission
  onSubmit() {

    // Prepare the data payload
    const payload = { message: this.userInput };
    this.messages.push("You: "+this.userInput);
    this.thinking=true;
    this.autoScroll();
    // Send the POST requestq
    this.appService.recieveUserInput(payload).subscribe(res=> { this.result = res; });
    console.log(this.result);
    this.messages.push("ChatBot: "+this.result);
    this.thinking=false;
    console.log(payload);
  }
  ngAfterViewChecked(): void {
    this.autoScroll();
  }
  private autoScroll(): void {
    const chatBoxElement = this.chatBox?.nativeElement;
    if (chatBoxElement) {
      chatBoxElement.scrollTop = chatBoxElement.scrollHeight;
    }
  }
}