import { Component } from '@angular/core';
import { Chat } from '../models/chat.model';
import { ChatService } from '../services/chatbot.services';
import { ChatCommunicationService } from '../services/chat_service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.css',
  standalone:false
})
export class SidebarComponent {
  // Array of chat objects (you can fetch this from an API or service)
  chats:Chat[]=[];

  constructor(private chatService:ChatService, private chatCommunicationService: ChatCommunicationService,private authService:AuthService) {}

  ngOnInit(): void {
    this.chatCommunicationService.getUserChats(this.authService.getUserID()).subscribe((chats: Chat[]) => {
      this.chats = chats;
      console.log(this.chats);
    });
    console.log(this.chats)
    this.chatCommunicationService.newChat$.subscribe(res => {
      let chatArray: Chat[] = [];
      this.chatCommunicationService.getUserChats(this.authService.getUserID()).subscribe((chats: Chat[]) => {
        this.chats = chats;
        console.log(this.chats);
      });      /*
        this.chatCommunicationService.newChat$.subscribe(res => {
///       ZAMENITI SA PRAVIM USEROM
//       let chatArray: Chat[] = [];

      this.chatCommunicationService.getUserChats(this.authService.getUserID()
        ).subscribe((chats: Chat[]) => {
        chatArray = chats;
        console.log(chatArray);  // Now you have the Chat[] in chatArray
      });
      */
    });
  }
  addChat()
  {
    const uuid = crypto.randomUUID();
    console.log("UUID: ",uuid) 
    // ovo bi trebalo da kreira novi chat ali u chatCommunicationService-u i da ih tamo skadisti
    this.chats.push(this.chatCommunicationService.startNewChat(1, uuid));
    // ovo bi trebalo da izvuce te chatove iz tog servisa i da ih displajuje kod sebe
  }
}
