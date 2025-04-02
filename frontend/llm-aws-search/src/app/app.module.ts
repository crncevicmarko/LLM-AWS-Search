import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppComponent } from './app.component';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { MarkdownDisplayComponent } from './markdown-display/markdown-display.component';
import { ChatbotComponent } from './chatbot/chatbot.component';
import { routes } from './app.routes';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { SidebarComponent } from './sidebar/sidebar.component';

@NgModule({
  declarations: [
    AppComponent,
    MarkdownDisplayComponent,
    ChatbotComponent,  // Declare your components here
    SidebarComponent,
    
  ],
  imports: [
    BrowserModule,  // Import essential modules here
    HttpClientModule,  // Import HttpClientModule to enable HTTP requests
    FormsModule,
    RouterModule.forRoot(routes),
    MatButtonModule,
    MatInputModule,
    MatIconModule,
    MatCardModule,
    MatProgressSpinnerModule
  ],
  providers: [],
  bootstrap: [AppComponent]  // Specify your root component
})
export class AppModule { }
