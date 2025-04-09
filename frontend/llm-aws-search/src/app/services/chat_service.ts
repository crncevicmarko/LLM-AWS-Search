import { Injectable } from '@angular/core';
import { map, Observable, ReplaySubject, Subject } from 'rxjs';
import { Chat } from '../models/chat.model';
import { ChatService } from './chatbot.services';
import { environment } from '../../enviroments/enviroment';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class ChatCommunicationService {
  private chats: Chat[] = [];

  // Subjects for communication
  private newChatSubject = new ReplaySubject();
  private userInputSubject = new ReplaySubject<{ input: string, chatId: string }>(1);
  private apiHost=environment.apiUrl;
  newChat$ = this.newChatSubject.asObservable();
  userInput$ = this.userInputSubject.asObservable();
  headers: HttpHeaders = new HttpHeaders({ 'Content-Type' : 'application/json', 'Accept':'*/*'})

  constructor(private chatbotService: ChatService,private http:HttpClient) {}

  private generateRandomName(length: number): string {
    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
    let result = '';
    for (let i = 0; i < length; i++) {
      const randomIndex = Math.floor(Math.random() * characters.length);
      result += characters[randomIndex];
    }
    return result;
  }

  startNewChat(userId: number, uuid: string): Chat {
    console.log("usli u startNewChat")
    const randomName = this.generateRandomName(10);
    const newChat: Chat = { id: uuid, name: "New Chat - "+randomName, userId };
    this.chats.push(newChat);
    return newChat;
  }

  getAllChats(): Chat[] {

    return this.chats;
  }
  getUserChats(userId: string): Observable<Chat[]> {
    return this.http.get<any>(`${this.apiHost}/chats-by-user?user_id=` + userId, { headers: this.headers })
      .pipe(
        map((response) => {
          // Ensure the 'response' object contains an array
          const chats = response.response;
          if (Array.isArray(chats)) {
            return chats.map(chat => ({
              id: chat.chat_id,        // Map 'chat_id' to 'id'
              userId: chat.user_id,    // Map 'user_id' to 'userId'
              name: chat.title,        // Map 'title' to 'name'
            }));
          } else {
            // Handle case where the 'response' is not an array
            console.error('Chats data is not an array', response);
            return []; // Return an empty array in case of error
          }
        })
      );
  }
  
  
  sendUserInput(input: string, chatId: string) {
    console.log("Usli u send user input")
    this.userInputSubject.next({ input, chatId });
  }
}
