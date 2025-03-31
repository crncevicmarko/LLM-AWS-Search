import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Injectable } from "@angular/core";
import { environment } from '../../enviroments/enviroment';

@Injectable({
    providedIn: 'root'
  })
export class AppService{
    constructor(private http: HttpClient) { }
    apiHost: string=environment.apiUrl;
    headers: HttpHeaders = new HttpHeaders({ 'Content-Type' : 'application/json'})
    recieveUserInput(text: any): Observable<any>{
        return this.http.post<any>(this.apiHost+ '/test-chatbot',text, {headers: this.headers})
    }
    }