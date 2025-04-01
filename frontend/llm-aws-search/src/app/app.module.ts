import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppComponent } from './app.component';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { MarkdownDisplayComponent } from './markdown-display/markdown-display.component';
import { ChatbotComponent } from './chatbot/chatbot.component';
import { routes } from './app.routes';

@NgModule({
  declarations: [
    AppComponent,
    MarkdownDisplayComponent,
    ChatbotComponent  // Declare your components here
  ],
  imports: [
    BrowserModule,  // Import essential modules here
    HttpClientModule,  // Import HttpClientModule to enable HTTP requests
    FormsModule,
    RouterModule.forRoot(routes)
  ],
  providers: [],
  bootstrap: [AppComponent]  // Specify your root component
})
export class AppModule { }
