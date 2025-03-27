import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Injectable } from "@angular/core";

@Injectable({
    providedIn: 'root'
  })
export class AppService{
    constructor(private http: HttpClient) { }
    apiHost:string="https://pyop5xjxr5.execute-api.eu-west-1.amazonaws.com/prod";
    headers: HttpHeaders = new HttpHeaders({ 'Content-Type' : 'application/json'})
    recieveUserInput(message: any): Observable<any>{
        console.log(this.headers)
        return this.http.post<any>(this.apiHost+ '/test-chatbot',message, {headers: this.headers})
    }
    }