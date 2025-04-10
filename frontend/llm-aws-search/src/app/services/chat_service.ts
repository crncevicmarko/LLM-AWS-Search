import { Injectable } from '@angular/core';
import { generate, map, Observable, ReplaySubject, Subject } from 'rxjs';
import { Chat } from '../models/chat.model';
import { ChatService } from './chatbot.services';
import { environment } from '../../enviroments/enviroment';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';

@Injectable({
  providedIn: 'root'
})
export class ChatCommunicationService {
  private chats: Chat[] = [];

  private newChatSubject = new ReplaySubject();
  private userInputSubject = new ReplaySubject<{ input: string, chatId: string }>(1);
  private refreshSidebarSubject = new Subject<void>();


  private apiHost=environment.apiUrl;
  newChat$ = this.newChatSubject.asObservable();
  userInput$ = this.userInputSubject.asObservable();
  refreshSidebar$ = this.refreshSidebarSubject.asObservable();

  constructor(private http:HttpClient) {}

  headers: HttpHeaders = new HttpHeaders({
    'Content-Type': 'application/json',
    'Accept': '*/*'
  });

  triggerSidebarRefresh() {
    console.log("Usli u triggerSidebarRefresh u chat_service")
    this.refreshSidebarSubject.next();
  }

  startNewChat(userId: number, uuid: string): Chat {
    console.log("usli u startNewChat")
    const newChat: Chat = { id: uuid, name: "New Chat", userId };
    this.chats.push(newChat);
    this.newChatSubject.next(newChat);
    return newChat;
  }

  getAllChatsTest(): Chat[] {
    // ovde ce da ide GET https koji ce da fecuje sve chatove i smestace ih u this.chats listu. mora tako zato sto je sidebar komponenta postavljena u chatbotpge componetnu, i kada se kreira refresuje ta stranica refersuje se i sidebar sto je no bueno.
    console.log("Usli u getAllChats")
    const ampleChats: Chat[] = [
      {
        id: 'bfe94170-b955-47a7-9d94-86e2891dd183',
        name: 'New Chat - Alpha',
        userId: 10
      },
      {
        id: 'b2c3d4e5-f6a7-8901-2345-bcdefa234567',
        name: 'New Chat - Bravo',
        userId: 10
      },
      {
        id: 'c3d4e5f6-a7b8-9012-3456-cdefab345678',
        name: 'New Chat - Charlie',
        userId: 10
      },
      {
        id: 'd4e5f6a7-b8c9-0123-4567-defabc456789',
        name: 'New Chat - Delta',
        userId: 10
      },
      {
        id: 'e5f6a7b8-c9d0-1234-5678-efabcd567890',
        name: 'New Chat - Echo',
        userId: 10
      }
    ];
    this.chats = ampleChats
    return this.chats
  }
  
  createNewChat(userId: number, uuid: string): Chat[] {
    console.log("usli u startNewChat")
    const newChat: Chat = { id: uuid, name: "New Chat", userId };
    this.chats.push(newChat);
    console.log("newly created chat:"+newChat)
    return this.chats;
  }

  getAllChats(user_id: string, callback: (chats: Chat[]) => void): void {
    
    this.getUserChats(user_id).subscribe((response: any) => {
      // Map the response data like in the first example
      this.chats = response.response.map((chat: any) => ({
        id: chat.chat_id,      // Map 'chat_id' to 'id'
        userId: chat.user_id,  // Map 'user_id' to 'userId'
        name: chat.title,      // Map 'title' to 'name'
      }));
      
      console.log("Mapped chats:");
      console.log(this.chats);  // Logs the mapped chats data
  
      // Call the callback function with the updated chats data
      callback(this.chats);
    }, (error) => {
      console.error('Error fetching chats', error);
      callback([]);  // Return an empty array in case of error
    });
  }


  getUserChats(userId: string): Observable<Chat[]> {
    console.log(`${this.apiHost}/chats-by-user?user_id=` + userId)
    const params = new HttpParams().set('user_id', userId);
    const url = `${this.apiHost}/chats-by-user?user_id=${userId}`;
    return this.http.get<any>(url);
  }

  saveChat(userId:string,prompt:string,chatId:string):any{
    const chat=
    {
      user_id:userId,
      chat_id:      chatId,
      text:prompt

    }
    console.log(chat);
   return this.http.post<any>(this.apiHost+"/generate-title",chat,{});
  }
  
  // sendUserInput(input: string, chatId: string) {
  //   console.log("Usli u send user input")
  //   this.userInputSubject.next({ input, chatId });
  // }
  // getChatNameLocally(chatId:any)
  // {
  //   const chat = this.chats.find(chat => chat.id === chatId);
  //   if (chat) {
  //     console.log(`Chat found: ${chat.name}`);
  //     return chat.name==="New Chat";
  //   } else {
  //     console.log('Chat not found');
  //     alert("Failed to initialize chat! Please add a new chat!");
  //     return false;
  //   }
  // }
  // refreshPage()
  // {
  //   this.refreshPageSubject.next("");
  // }

}
