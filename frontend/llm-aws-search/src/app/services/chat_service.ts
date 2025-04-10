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
  private refreshPageSubject = new ReplaySubject();

  private apiHost=environment.apiUrl;
  newChat$ = this.newChatSubject.asObservable();
  userInput$ = this.userInputSubject.asObservable();
 refreshPage$=this.refreshPageSubject.asObservable();
  headers: HttpHeaders = new HttpHeaders({
    'Content-Type': 'application/json',
    'Accept': '*/*'
  });
  constructor(private chatbotService: ChatService,private http:HttpClient, private route:ActivatedRoute) {}

  private generateRandomName(length: number): string {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
    let result = '';
    for (let i = 0; i < length; i++) {
      const randomIndex = Math.floor(Math.random() * characters.length);
      result += characters[randomIndex];
    }
    return result;
  }



  startNewChat(userId: number, uuid: string): Chat[] {
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
      /*.pipe(
        map((response) => {
          const chats = response.response;
          console.log(response)
          if (Array.isArray(chats)) {
            return chats.map(chat => ({
              id: chat.chat_id,      
              userId: chat.user_id,    
              name: chat.title,       
            }));
          } else {

            console.error('Chats data is not an array', response);
            return [];
          }
        })
      );*/
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
  
  sendUserInput(input: string, chatId: string) {
    console.log("Usli u send user input")
    this.userInputSubject.next({ input, chatId });
  }
  getChatNameLocally(chatId:any)
  {
    const chat = this.chats.find(chat => chat.id === chatId);
    if (chat) {
      console.log(`Chat found: ${chat.name}`);
      return chat.name==="New Chat";
    } else {
      console.log('Chat not found');
      alert("Failed to initialize chat! Please add a new chat!");
      return false;
    }
  }
  refreshPage()
  {
    this.refreshPageSubject.next("");
  }

}
