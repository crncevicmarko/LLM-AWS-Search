import { Routes } from '@angular/router';
import { ChatbotComponent } from './chatbot/chatbot.component';
import { AppComponent } from './app.component';

export const routes: Routes = [
  // Redirect the root route ("/") to the chat route ("/chat")
  { path: '', redirectTo: '/chat', pathMatch: 'full' },
  
  // Define the route for the chat page
  { path: 'chat', component: ChatbotComponent },
  
  // You can add additional routes here if you want to handle other pages
  
  // Example for a 404 route
  { path: '**', redirectTo: '/chat' },  // Redirect unknown routes to /chat
];
