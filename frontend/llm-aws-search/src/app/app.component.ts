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
constructor(private appService: AppService) { }


  // Function to handle form submission
  onSubmit() {

    // Prepare the data payload
    const payload = { input: this.userInput };

    // Send the POST request
    this.appService.recieveUserInput(payload).subscribe(res=> { this.result = res; });
    
    console.log(payload);
  }
}