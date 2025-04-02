import { Component } from '@angular/core';
import { Chat } from '../models/chat.model';
import { ChatService } from '../services/chatbot.services';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.css',
  standalone:false
})
export class SidebarComponent {
  // Array of chat objects (you can fetch this from an API or service)
  chats:Chat[]=[];


  constructor(private chatService:ChatService) { }

  ngOnInit(): void {
    this.chats=this.chatService.getAllChats(1);
    }
  addChat()
  {
    this.chats=this.chatService.startNewChat(1);
  }
  changeName(newName:string)
  {
    const chatToUpdate=this.chats.find(chat => chat.name === 'New Chat');
    
    if (chatToUpdate) {
      chatToUpdate.name = newName;
      console.log('Updated chat name:', chatToUpdate);
    } else {
      console.log('Chat with name "New Chat" not found');
    }  
  }
}
