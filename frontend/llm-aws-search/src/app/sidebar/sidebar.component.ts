import { Component } from '@angular/core';
import { Chat } from '../models/chat.model';
import { ChatService } from '../services/chatbot.services';
import { ChatCommunicationService } from '../services/chat_service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.css',
  standalone:false
})
export class SidebarComponent {
  // Array of chat objects (you can fetch this from an API or service)
  chats:Chat[]=[];

  constructor(private chatService:ChatService, private chatCommunicationService: ChatCommunicationService) {}

  ngOnInit(): void {
    this.chatCommunicationService.newChat$.subscribe(res => {
      // ovde bi trebali da prikazujemo samo novo kreirane chatove iz chatCommunicationService-a
      this.chats = this.chatCommunicationService.getAllChats();
    });
  }
  addChat()
  {
    const uuid = crypto.randomUUID();
    console.log("UUID: ",uuid) 
    // ovo bi trebalo da kreira novi chat ali u chatCommunicationService-u i da ih tamo skadisti
    this.chatCommunicationService.startNewChat(1, uuid);
    // ovo bi trebalo da izvuce te chatove iz tog servisa i da ih displajuje kod sebe
    this.chats = this.chatCommunicationService.getAllChats();
  }
}
