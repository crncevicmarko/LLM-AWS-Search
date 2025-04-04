import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable,of } from 'rxjs';
import { Injectable, Query } from "@angular/core";
import { environment } from '../../enviroments/enviroment';
import { Chat } from '../models/chat.model';
@Injectable({
    providedIn: 'root'
  })
export class ChatService{
    constructor(private http: HttpClient) { }
    apiHost: string=environment.apiUrl;
    headers: HttpHeaders = new HttpHeaders({ 'Content-Type' : 'application/json'})
    recieveUserInput(query: any): Observable<any>{
      console.log(query);
      const messageContent = query.message;
      const userMessage = {
        text: messageContent
      };
      
        return this.http.post<any>(this.apiHost+ '/test-chatbot',userMessage, {headers: this.headers})
    }
    getAllChats(userId:any): Chat[] {
      const chats:Chat[] = [
        { userId:1,name: 'Chat 1',id:1,chatHistory:[]},
        {userId:1,name: 'Chat 2',id:2,chatHistory:[]},
        {userId:1,name: 'Chat 3',id:3,chatHistory:[] },
        { userId:1,name: 'Chat 4',id:4,chatHistory:[] }
      ];
      return chats;
    }
    startNewChat(userId:any):Chat[]
    {
      const chats:Chat[] = [
        { userId:1,name: 'Chat 1',id:1,chatHistory:[]},
        {userId:1,name: 'Chat 2',id:2,chatHistory:[]},
        {userId:1,name: 'Chat 3',id:3,chatHistory:[] },
        { userId:1,name: 'Chat 4',id:4,chatHistory:[] }
      ];
      chats.push({userId:1,name:'New Chat',id:5,chatHistory:[]})
      console.log(chats);
      return chats;
    }

    }