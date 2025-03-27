import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Injectable } from "@angular/core";

@Injectable({
    providedIn: 'root'
  })
export class AppService{
    constructor(private http: HttpClient) { }
    apiHost:string="https://4ii70rdoj7.execute-api.eu-north-1.amazonaws.com/";
    headers: HttpHeaders = new HttpHeaders({ 'Content-Type' : 'application/json'})
    recieveUserInput(message: any): Observable<any>{
        console.log(this.headers)
        return this.http.post<any>(this.apiHost+ 'retrieveUserInput',message, {headers: this.headers})
    }
    }