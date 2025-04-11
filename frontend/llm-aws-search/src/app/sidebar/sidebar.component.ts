import { Component } from '@angular/core';
import { Chat } from '../models/chat.model';
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

  constructor(private chatCommunicationService: ChatCommunicationService,private authService:AuthService, private router: Router) {}

  ngOnInit(): void {
    this.userAuthData();

    this.chatCommunicationService.refreshSidebar$.subscribe(() => {
      console.log("Usli u ngOnInit od side bara u refreshSidebar")
    })
 
    // this.chatCommunicationService.getAllChats(this.user_id,(chats:any) => {
    //   this.chats=chats;
    // });
    // // console.log(this.user_id)
    // // console.log(this.chats)
    // this.chatCommunicationService.newChat$.subscribe(res => {
    //   this.chatCommunicationService.getAllChats(this.user_id,(chats:any) => {
    //     this.chats=chats;
    //   });
    // });
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
    this.startNewChat(1, uuid)
    this.router.navigate(['chat/', uuid]);
  }

  // addChat()
  // {
  //   const uuid = crypto.randomUUID();
  //   console.log("UUID: ",uuid) 
  //   console.log(this.chats)
  //   this.chats.push(this.chatCommunicationService.startNewChat(this.user_id, uuid));
  //   console.log(this.chats);  
  //   this.router.navigate(['chat/', uuid]);
  // }

  // loadChats(){
  //   // this.chats = this.chatCommunicationService.getAllChatsTest()
  //   this.chatCommunicationService.getAllChats(this.user_id,(chats:any) => {
  //     this.chats=chats;
  //   });
  // }

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
