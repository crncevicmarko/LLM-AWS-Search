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
  private refreshSidebarSubject = new Subject<void>();


  newChat$ = this.newChatSubject.asObservable();
  userInput$ = this.userInputSubject.asObservable();
  refreshSidebar$ = this.refreshSidebarSubject.asObservable();

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

  triggerSidebarRefresh() {
    console.log("Usli u triggerSidebarRefresh u chat_service")
    this.refreshSidebarSubject.next();
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
    const ampleChats: Chat[] = [
      {
        id: 'bfe94170-b955-47a7-9d94-86e2891dd183',
        name: 'New Chat - Alpha',
        userId: 10
      },
      {
        id: 'b2c3d4e5-f6a7-8901-2345-bcdefa234567',
        name: 'New Chat - Bravo',
        userId: 10
      },
      {
        id: 'c3d4e5f6-a7b8-9012-3456-cdefab345678',
        name: 'New Chat - Charlie',
        userId: 10
      },
      {
        id: 'd4e5f6a7-b8c9-0123-4567-defabc456789',
        name: 'New Chat - Delta',
        userId: 10
      },
      {
        id: 'e5f6a7b8-c9d0-1234-5678-efabcd567890',
        name: 'New Chat - Echo',
        userId: 10
      }
    ];
    this.chats = ampleChats
    return this.chats;
  }

  sendUserInput(input: string, chatId: string) {
    console.log("Usli u send user input")
    this.userInputSubject.next({ input, chatId });
  }
}
