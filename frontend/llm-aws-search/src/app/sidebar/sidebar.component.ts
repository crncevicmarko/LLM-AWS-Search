import { Component } from '@angular/core';
import { Chat } from '../models/chat.model';
import { ChatCommunicationService } from '../services/chat_service';
import { AuthService } from '../services/auth.service';
import { Router,NavigationEnd,Event as RouterEvent} from '@angular/router';
import { filter } from 'rxjs';


@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrl: './sidebar.component.css',
  standalone:false
})
export class SidebarComponent {
  // Array of chat objects (you can fetch this from an API or service)
  chats:Chat[]=[];
  user_id: any;
  isLoggedIn: boolean = false

  constructor(private chatCommunicationService: ChatCommunicationService,private authService:AuthService, private router: Router) {}

  ngOnInit(): void {
    this.userAuthData();

    this.chatCommunicationService.refreshSidebar$.subscribe(() => {
      console.log("Usli u ngOnInit od side bara u refreshSidebar")
    })
 
    this.chatCommunicationService.getAllChats(this.user_id,(chats:any) => {
      this.chats=chats;
    });
    
    //console.log(this.chatCommunicationService.getAllChats(this.user_id))
    this.chatCommunicationService.newChat$.subscribe(res => {
      this.chatCommunicationService.getAllChats(this.user_id,(chats:any) => {
        this.chats=chats;
      });
    });

    this.chatCommunicationService.refreshSidebar$.subscribe(res=>{
      window.location.reload();
      });
    
  }

  userAuthData():void {
    const token = this.authService.getAccessTokenFromLocalStorage();
    console.log("Token: ", token)
    this.user_id = this.authService.getUserID();
    if (token) this.isLoggedIn = true;
    else this.isLoggedIn = false;
  }
  addChat() {
    const uuid = crypto.randomUUID();
    console.log("Generated UUID:", uuid);
  
    const navSub = this.router.events
    .pipe(
      filter((event: RouterEvent): event is NavigationEnd => event instanceof NavigationEnd)
    )
    .subscribe(() => {
      setTimeout(() => {
        this.chats = this.chatCommunicationService.startNewChat(this.user_id, uuid);
        console.log("Chats after route loaded:", this.chats);
        navSub.unsubscribe();
      }, 1000);
    });
  
    this.router.navigate(['chat', uuid]);
  }

  // refresh(){
  //   this.chatCommunicationService.refreshSidebar$.subscribe()
  // }

}
