import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { AppService } from './services/app.services';
@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
  standalone:false
})
export class AppComponent {
  title = 'llm-aws-search';

userInput: string = ''; // Variable to bind input value
result:string='';
messages:string [] = [];  // Array to store the chat messages
constructor(private appService: AppService) { }


  // Function to handle form submission
  onSubmit() {

    // Prepare the data payload
    const payload = { message: this.userInput };
    this.messages.push("You: "+this.userInput);
    // Send the POST request
    this.appService.recieveUserInput(payload).subscribe(res=> { this.result = res; });
    console.log(this.result);
    this.messages.push("ChatBot: "+this.result);
    console.log(payload);
  }
}