import { Injectable } from '@angular/core';
import { ReplaySubject, Subject } from 'rxjs';
import { Chat } from '../models/chat.model';
import { ChatService } from './chatbot.services';

@Injectable({
  providedIn: 'root'
})
export class ChatCommunicationService {
  private chats: Chat[] = [];

  // Subjects for communication
  private newChatSubject = new ReplaySubject();
  private userInputSubject = new ReplaySubject<{ input: string, chatId: string }>(1);

  newChat$ = this.newChatSubject.asObservable();
  userInput$ = this.userInputSubject.asObservable();

  constructor(private chatbotService: ChatService) {}

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
    this.newChatSubject.next(newChat);
    return newChat;
  }

  getAllChats(): Chat[] {
    // ovde ce da ide GET https koji ce da fecuje sve chatove i smestace ih u this.chats listu. mora tako zato sto je sidebar komponenta postavljena u chatbotpge componetnu, i kada se kreira refresuje ta stranica refersuje se i sidebar sto je no bueno.
    console.log("Usli u getAllChats")
    return this.chats;
  }

  sendUserInput(input: string, chatId: string) {
    console.log("Usli u send user input")
    this.userInputSubject.next({ input, chatId });
  }
}
