import { Component } from '@angular/core';
import { Chat } from '../models/chat.model';
import { ChatService } from '../services/chatbot.services';
import { ChatCommunicationService } from '../services/chat_service';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';


@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.css',
  standalone:false
})
export class SidebarComponent {
  // Array of chat objects (you can fetch this from an API or service)
  chats:Chat[]=[];
  user_id: any;
  isLoggedIn: boolean = false

  constructor(private chatCommunicationService: ChatCommunicationService,private authService:AuthService) {}

  ngOnInit(): void {
    this.loadChats();
    this.userAuthData();
    // this.chatCommunicationService.newChat$.subscribe(res => {
      // ovde bi trebali da prikazujemo samo novo kreirane chatove iz chatCommunicationService-a
      // this.chats = this.chatCommunicationService.getAllChats();
    // });

    this.chatCommunicationService.refreshSidebar$.subscribe(() => {
      console.log("Usli u ngOnInit od side bara u refreshSidebar")
    })
 
    this.chatCommunicationService.getAllChats(this.user_id,(chats:any) => {
      this.chats=chats;
    });
    console.log(this.user_id)
    console.log(this.chats)
    this.chatCommunicationService.newChat$.subscribe(res => {
      this.chatCommunicationService.getAllChats(this.user_id,(chats:any) => {
        this.chats=chats;
      });
    });
  }

  userAuthData():void {
    const token = this.authService.getAccessTokenFromLocalStorage();
    console.log("Token: ", token)
    this.user_id = this.authService.getUserID();
    if (token) this.isLoggedIn = true;
    else this.isLoggedIn = false;
  }
  addChat()
  {
    const uuid = crypto.randomUUID();
    console.log("UUID: ",uuid) 
    // ovo bi trebalo da kreira novi chat ali u chatCommunicationService-u i da ih tamo skadisti
    // this.chatCommunicationService.startNewChat(1, uuid);
    // ovo bi trebalo da izvuce te chatove iz tog servisa i da ih displajuje kod sebe
    // this.chats = this.chatCommunicationService.getAllChats();
    this.startNewChat(1, uuid)
  }

  // addChat()
  // {
  //   const uuid = crypto.randomUUID();
  //   console.log("UUID: ",uuid) 
  //   console.log(this.chats)
  //   this.chats=    this.chatCommunicationService.startNewChat(this.user_id, uuid);
  //   console.log(this.chats);  
  //   this.router.navigate(['chat/', uuid]);

  // }

  loadChats(){
    // this.chats = this.chatCommunicationService.getAllChats()getAllChatsTest
    this.chats = this.chatCommunicationService.getAllChatsTest()
  }

  startNewChat(userId: number, uuid: string): Chat {
    console.log("usli u startNewChat")
    const newChat: Chat = { id: uuid, name: "New Chat", userId };
    this.chats.push(newChat);
    return newChat;
  }

  // refresh(){
  //   this.chatCommunicationService.refreshSidebar$.subscribe()
  // }

}
