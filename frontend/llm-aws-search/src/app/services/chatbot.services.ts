import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable,of } from 'rxjs';
import { Injectable, Query } from "@angular/core";
import { environment } from '../../enviroments/enviroment';
import { Chat } from '../models/chat.model';
@Injectable({
    providedIn: 'root'
  })
export class ChatService{
    private chats: Chat[] = [];
    constructor(private http: HttpClient) { }
    apiHost: string=environment.apiUrl;
    dinamoDBUrlGetChatHistory: string=environment.dinamoDBUrlGetChatHistory;
    headers: HttpHeaders = new HttpHeaders({ 'Content-Type' : 'application/json', 'Accept':'*/*'})
    recieveUserInput(query: any, chatHistory: any): Observable<any>{
      console.log(query);
      const messageContent = query.message;
      const userMessage = {
        chat_history: chatHistory,
        user_input: messageContent
      };
      
        return this.http.post<any>(this.apiHost+ '/test-chatbot',userMessage, {headers: this.headers})
    }
    
    getChatsById(chat_id: string): Observable<any> {
      const params = new HttpParams().set('chat_id', chat_id);
    
      return this.http.get(this.dinamoDBUrlGetChatHistory, {
        headers: this.headers,
        params,
        responseType: 'json'
      });
    }

    // getChatById(chat_id:any): Observable<any> {
    //   const url = `${this.dinamoDBUrlGetChatHistory}${chat_id}`;
    //   console.log("Url: ",url)
    //   return this.http.get(url, {
    //     headers: this.headers,
    //     responseType: 'json'
    //   });
    // }
    private generateRandomName(length: number): string {
      const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz';
      let result = '';
      for (let i = 0; i < length; i++) {
        const randomIndex = Math.floor(Math.random() * characters.length);
        result += characters[randomIndex];
      }
      return result;
    }

    startNewChat(userId:any, chat_id:any):Chat[]
    {
      const randomName = this.generateRandomName(10);
      this.chats.push({userId:1,name:randomName,id:chat_id})
      console.log(this.chats);
      return this.chats;
    }

    }