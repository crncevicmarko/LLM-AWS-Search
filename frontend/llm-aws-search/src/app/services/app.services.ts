import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Injectable } from "@angular/core";

@Injectable({
    providedIn: 'root'
  })
export class AppService{
    constructor(private http: HttpClient) { }
    apiHost:string="https://2he3wa0mf3.execute-api.eu-west-1.amazonaws.com";
    headers: HttpHeaders = new HttpHeaders({ 'Content-Type' : 'application/json'})
    recieveUserInput(message: any): Observable<any>{
        console.log(message)
        return this.http.post<any>(this.apiHost+ '/test-stage-1',message, {headers: this.headers})
    }
    }