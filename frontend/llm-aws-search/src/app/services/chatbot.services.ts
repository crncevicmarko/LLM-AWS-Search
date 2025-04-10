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
    headers: HttpHeaders = new HttpHeaders({ 'Content-Type' : 'application/json', 'Accept':'*/*'})
    recieveUserInput(query: any, chat_history: any): Observable<any>{
      console.log("Query: ",query);
      console.log("Chat History: ",chat_history)
      const messageContent = query.message;
      const userMessage = {
        user_input: messageContent,
        chat_history: chat_history
      };

        return this.http.post<any>(this.apiHost+ '/test-chatbot',userMessage, {headers: this.headers})
    }

    getChatsById(chat_id: string): Observable<any> {
      const params = new HttpParams().set('chat_id', chat_id);

      return this.http.get(this.apiHost+ '/get-messages', {
        headers: this.headers,
        params,
        responseType: 'json'
      });
    }

    postNewChatMessage(user_id: string, chat_id: string, userMessage: string, chatMessage: string) {
      const body = {
        user_id: user_id,
        chat_id: chat_id,
        user_message: userMessage,
        chat_message: chatMessage
      };
      console.log("Body: ", body)  
      return this.http.post<any>(this.apiHost+ '/save-message', body, {headers: this.headers});
    }

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

    reportBug(bugData: { email: string; description: string }): Observable<any> {
      console.log("Usaoo")
      return this.http.post<any>('https://ax08zk1nzj.execute-api.eu-west-1.amazonaws.com/prod/send-bug-report', bugData);
    }

    }
