import { Injectable } from '@angular/core';
import {
  AuthUser,
  getCurrentUser,
  signOut,
  fetchAuthSession,
  AuthTokens,
  decodeJWT,
} from 'aws-amplify/auth';
import { BehaviorSubject, Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private loggedInSubject = new BehaviorSubject<boolean>(false);
  constructor() {}

  isUserLoggedIn(): Observable<boolean> {
    return this.loggedInSubject.asObservable();
  }
  logIn() {
    this.loggedInSubject.next(true); 
  }

  logOut() {
    this.loggedInSubject.next(false); 
  }
  
  async getCurrentUser(): Promise<AuthUser> {
    return await getCurrentUser();
  }

  async getCurrentSession(): Promise<AuthTokens | undefined> {
    return (await fetchAuthSession()).tokens;
  }

  public getUserID(): string {
    try {
      const decodedToken: any = decodeJWT(
        this.getAccessTokenFromLocalStorage() || ''
      );
      const roles: string | undefined = decodedToken['payload']['sub'];
      if (roles && roles.length > 0) {
        return roles;
      } else {
        return '';
      }
    } catch (error) {
      console.error('Error decoding accessToken:', error);
      return '';
    }
  }
  public getEmail(): string {
    try {
      const decodedToken: any = decodeJWT(
        this.getAccessTokenFromLocalStorage() || ''
      );
      const roles: string | undefined = decodedToken['payload']['username'];
      if (roles && roles.length > 0) {
        return roles;
      } else {
        return '';
      }
    } catch (error) {
      console.error('Error decoding accessToken:', error);
      return '';
    }
  }
  signOut() {
      localStorage.removeItem('accessToken'); 
    }

  public getAccessTokenFromLocalStorage(): string | null {
    const token = localStorage.getItem('accessToken');
    if (token) {
      return token;
    }
    return null;
  
  }
}