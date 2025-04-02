import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Injectable, Query } from "@angular/core";
import { environment } from '../../enviroments/enviroment';

@Injectable({
    providedIn: 'root'
  })
export class AppService{
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
    }