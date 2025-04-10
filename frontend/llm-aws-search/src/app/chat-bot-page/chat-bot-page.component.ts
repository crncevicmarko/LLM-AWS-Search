import { AfterViewChecked, Component,ElementRef,OnInit,ViewChild } from '@angular/core';
import { ChatService } from '../services/chatbot.services';
import { ChangeDetectorRef } from '@angular/core';
import { MarkdownDisplayComponent } from '../markdown-display/markdown-display.component';
import { ActivatedRoute, Router } from '@angular/router';
import { Chat } from '../models/chat.model';
import { timestamp } from 'rxjs';
import { ChatCommunicationService } from '../services/chat_service';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-chat-bot-page',
  standalone: false,
  templateUrl: './chat-bot-page.component.html',
  styleUrl: './chat-bot-page.component.css'
})
export class ChatBotPageComponent {
  isLoggedIn: boolean = false;
  title = 'llm-aws-search';
thinking: boolean=false;
@ViewChild('chatBox') chatBox: ElementRef | undefined;
@ViewChild('chatInput') chatInput: ElementRef | undefined;
userInput: string = '';
userMessages:string [] = [];
botMessages:string[]=[];
time:string=new Date().toLocaleTimeString();
htmlContent:string="";
typingSpeed: number = 50;
chatId: any;
chatHistory: any;
chatPairs: { user: string, bot: string, timestamp: string }[] = [];
chatPairsClone: { user: string, bot: string, timestamp: string }[] = [];
user_id = "";
chat_history: any;
private pendingUserInput: string | null = null;
constructor(
  private chatService: ChatService,
  private chatCommunicationService: ChatCommunicationService,
  private cdRef: ChangeDetectorRef,
  private mdComp:MarkdownDisplayComponent,
  private route: ActivatedRoute,
  private authService: AuthService,
  private router: Router
) { }

  ngOnInit(): void {
    //user authentification for this page
    
    this.userAuthData();

    // ako je udjeno u drugi chat ili refresovana stranica trebala bi da se loduje cela istorija ponovo.
    this.sessionRefresh();

    this.route.paramMap.subscribe(params => {
      console.log("Usli u onInit u ChatBotPageComponent 1");
      this.chatId = params.get('id');
      this.loadChatData();
      
    });

    this.chatCommunicationService.userInput$.subscribe(({ input, chatId }) => {
      console.log("Usli u onInit u ChatBotPageComponent 2");
      this.userInput = input;
      this.cloneSubmit();
      // this.onSubmit();
    });
  }

  userAuthData():void {
    const token = this.authService.getAccessTokenFromLocalStorage();
    console.log("Token: ", token)
    this.user_id = this.authService.getUserID();
    if (token) this.isLoggedIn = true;
    else this.isLoggedIn = false;
  }

  sessionRefresh():void{
    sessionStorage.clear();
  }
  loadChatData(): void {
    console.log("ChatID kada vrsimo ucitavanje istorije: ", this.chatId)
    const storedChatHistory = sessionStorage.getItem(this.chatId);
    if (storedChatHistory) {
        console.log("Usli i session storage nije prazan")
        const chatData = JSON.parse(storedChatHistory);
        console.log("Chat Data iz local storage: ",chatData)

        this.chatPairs = chatData.chatPairs || [];
        console.log("Chat parovi iz local storage: ",this.chatPairs)
    }else{
      console.log("session storage je prazan")
      
      this.chatService.getChatsById(this.chatId).subscribe({
        next: (res) => {
          this.chatHistory = res.messages
          console.log("CHAT HISTORY: ",res.messages)
          this.chatPairs = this.chatHistory.map((chat: any) => ({
              user: chat.user_message,
              bot: chat.chat_message,
              timestamp: new Date(chat.timestamp * 1000).toLocaleTimeString()
          }));
          console.log("CHAT PAIRS: ", this.chatPairs)
          this.saveChatHistoryLocally();
        },
        error: err => {
          alert("Error getting bot response")
          console.error("Error getting bot response:", err);
          this.thinking = false;
        }
      });
    }
  }
  // cuva istoriju i nove vrednosti u local storage ili cash
  saveChatHistoryLocally() {
    console.log("Chat Pairs in saveChatHistoryLocally method: ", this.chatPairs)
    console.log("Chat Id preko kojeg ga cuva u session storage: ",this.chatId)
    const chatData = {
      chatPairs: this.chatPairs
    };
    // localStorage.setItem(`chat-${this.chatId}`, JSON.stringify(chatData));
    sessionStorage.setItem(this.chatId, JSON.stringify(chatData));
  }
  newValue = ''
  newCloneSubmitValue = ''

  // Function to handle form submission
  
  
  getFormattedChatHistory(): any[] {
    const storedChat = sessionStorage.getItem(this.chatId);
    let formattedChatHistory: any[] = [];
  
    if (storedChat && storedChat.trim() !== "") {
      try {
        const parsed = JSON.parse(storedChat);
        if (parsed.chatPairs && Array.isArray(parsed.chatPairs)) {
          formattedChatHistory = parsed.chatPairs.map((pair: any) => ({
            user_message: pair.user,
            chat_message: pair.bot
          }));
        }
      } catch (e) {
        console.error("Error parsing sessionStorage: ", e);
      }
    }
  
    return formattedChatHistory;
  
  }
  cloneSubmit(){
    const userMsg = this.userInput;
    this.userInput = ""; // obrisemo user text iz input polja kada se posalje zahtev
    this.thinking = true;

    // treba da se samo kreira novi zahtev koji ce da se sacuva u
    const formattedChatHistory = this.getFormattedChatHistory();

    this.chatService.recieveUserInput({ message: userMsg }, formattedChatHistory).subscribe(res => {
      const parsedResponse = this.mdComp.convertMarkdownToHTML(res.response);
      this.newValue = parsedResponse;
      console.log("Parsed Response: ", parsedResponse);
      const responseIndex = this.chatPairs.length;
      console.log("Response index: ", responseIndex)

      this.chatPairs.push({
        user: userMsg,
        bot: "", 
        timestamp: new Date().toLocaleTimeString()
      });
  

      this.simulateTyping(parsedResponse, responseIndex); 
    
      console.log("Updated Chat Pairs after bot response: ", this.chatPairs);
      
      // save new chat conversation to the DINAMO
      this.chatService.postNewChatMessage(this.user_id, this.chatId, userMsg, parsedResponse).subscribe({
        next: (response) => {
          console.log('Message successfully saved to DynamoDB:', response);
        },
        error: (err) => {
          console.error('Failed to save message to DynamoDB:', err);
        }
      });
    
      console.log("Updated newValue after response: ", this.newValue);
    });

    this.saveChatHistoryLocally();
  }

  onSubmit() {
    const userMsg = this.userInput;
    this.userInput = ""; // obrisemo user text iz input polja kada se posalje zahtev
    this.thinking = true;
    if((this.chatCommunicationService.getChatNameLocally(this.route.snapshot.paramMap.get('id'))))
      {
        console.log("new chat postoji");
        this.chatCommunicationService.saveChat(this.user_id,userMsg,this.chatId).subscribe();
        console.log("refresujem");
        this.chatCommunicationService.refreshPage();
        alert("Please refresh the page.");

      }
    const currentTime = new Date().toLocaleTimeString();
    const responseIndex = this.chatPairs.length;
    console.log("Response Index: ", responseIndex)
  
    console.log("Chat Pairs before update: ", this.chatPairs);
  
    this.chatPairs.push({
      user: userMsg,
      bot: "", 
      timestamp: currentTime
    });
  
    const formattedChatHistory = this.getFormattedChatHistory();

    this.chatService.recieveUserInput({ message: userMsg }, formattedChatHistory).subscribe(res => {
      const parsedResponse = this.mdComp.convertMarkdownToHTML(res.response);
      this.newValue = parsedResponse;
      console.log("Parsed Response: ", parsedResponse);
    
      this.simulateTyping(parsedResponse, responseIndex); 
      // this.chatPairs[responseIndex].bot = this.newValue
    
        console.log("Updated Chat Pairs after bot response: ", this.chatPairs);

        // ovde treba da se salje POST request do DINAMO-DB-a-------------------------------------------------
        this.chatService.postNewChatMessage(this.user_id, this.chatId, userMsg, parsedResponse).subscribe({
          next: (response) => {
            console.log('Message successfully saved to DynamoDB:', response);
          },
          error: (err) => {
            console.error('Failed to save message to DynamoDB:', err);
            // alert("Data is not successfuly saved"+ err)
          }
        }); 

        this.saveChatHistoryLocally();
      console.log("Updated Chat Pairs after bot response: ", this.chatPairs);
    
      this.chatService.postNewChatMessage(this.user_id, this.chatId, userMsg, parsedResponse).subscribe({
        next: (response) => {
          console.log('Message successfully saved to DynamoDB:', response);
        },
        error: (err) => {
          console.error('Failed to save message to DynamoDB:', err);
        }
      });
    
      this.saveChatHistoryLocally();
    
      console.log("Updated newValue after response: ", this.newValue);
    });
   
          
      }
    

  simulateTyping(response: string, responseIndex: number) {
    let words = response.split(' ');
    let currentWords = [];
    let index = 0;
    const wordsPerBatch = 5;
    const typingSpeed = 300;
    console.log("Chat Pairs in simulate typing: ", this.chatPairs[responseIndex].bot)
  
    const intervalId = setInterval(() => {
      currentWords.push(...words.slice(index, index + wordsPerBatch));
      this.chatPairs[responseIndex].bot = currentWords.join(" ");
      this.cdRef.detectChanges();
  
      index += wordsPerBatch;
      if (index >= words.length) {
        clearInterval(intervalId);
        this.thinking = false;
      }
    }, typingSpeed);
  }
  

  isSameAsLastPrompt(): boolean {

    return this.userMessages[this.userMessages.length-1] === this.userInput;
  }
  
  ngAfterViewChecked(): void {
    this.autoScroll();
  }
  resizeInput(inputElement: HTMLTextAreaElement): void {    
    inputElement.style.height = 'auto';

    inputElement.style.height = `${inputElement.scrollHeight}px`;

    if (inputElement.scrollHeight > 100) {
      inputElement.style.height = '100px'; // Max height, can be adjusted
    }
  }
  private autoScroll(): void {
    const chatBoxElement = this.chatBox?.nativeElement;
    if (chatBoxElement) {
      chatBoxElement.scrollTop = chatBoxElement.scrollHeight;
    }
  }

  logOut(): void {
    this.authService.signOut();
    this.router.navigate(['login']);
  }
}