import { AfterViewChecked, Component,ElementRef,OnInit,ViewChild } from '@angular/core';
import { ChatService } from '../services/chatbot.services';
import { ChangeDetectorRef } from '@angular/core';
import { MarkdownDisplayComponent } from '../markdown-display/markdown-display.component';
import { ActivatedRoute, Router } from '@angular/router';
import { Chat } from '../models/chat.model';
import { timestamp } from 'rxjs';
import { ChatCommunicationService } from '../services/chat_service';
import { AuthService } from '../services/auth.service';
// import { AuthService } from '../services/auth.service';

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
private initialized = false;
user_id = "";
chat_history: any;
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

    // Second subscription: input from ChatbotComponent
    this.chatCommunicationService.userInput$.subscribe(({ input, chatId }) => {
      console.log("Usli u onInit u ChatBotPageComponent 2");
      // this.chatId = chatId;
      this.userInput = input;

      if (this.router.url !== `/chat/${chatId}`) {
        this.router.navigate([`/chat/${chatId}`]);
      }

      console.log("Usli u chat-bot-page componentu:", "chat id:", this.chatId, " user input:", this.userInput);
      this.onSubmit();
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
    // const storedChatHistory = localStorage.getItem(`chat-${this.chatId}`);
    // if (!this.chatPairs || this.chatPairs.length === 0) {
    // const storedChatHistory = sessionStorage.getItem(`09e16992-880b-4ee0-b20f-af7f6baa8c00`);
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
      this.chatHistory = [
        {
        user_message: "give me tickets about retreveUserInput lambda",
        user_id: this.user_id,
        chat_message: `¡Hola! Estoy encantada de poder brindarte información sobre los tickets de Jira relevantes para tu solicitud sobre la función Lambda "retrieveUserInput".
        - **ID: SCRUM-17 Conectar la función Lambda AWS RetreveUserInput con el servicio Bedrock**
        Descripción: La tarea consiste en crear o actualizar una función Lambda de AWS para interactuar con el servicio AWS Bedrock. La función Lambda hará lo siguiente:
        - Recibir la entrada del usuario a través de una API Gateway.
        - Llamar al servicio Bedrock para generar incrustaciones o respuestas de texto en función de la entrada.
        - Si es aplicable, usar las incrustaciones para consultar una base de datos de vectores (por ejemplo, Pinecone).
        - Dar formato a los resultados en un formato amigable para el usuario.
        - Devolver la respuesta con formato al cliente.
        (https://jiralevi9internship2025.atlassian.net/browse/SCRUM-17)

        ¡Espero que esta información sobre los tickets de Jira relevantes haya sido útil! Si necesitas más detalles o tienes más preguntas, no dudes en hacérmelas saber. Estoy aquí para ayudarte en todo lo que pueda.`,
        chat_id: this.chatId,
        timestamp: 1744008177
      },
      {
        user_message: "what are the issues related to getMessages lambda",
        user_id: this.user_id,
        chat_message: `Sure! Here's a list of Jira tickets related to the Lambda function "getMessages":
          - **ID: SCRUM-25 Implement the Lambda getMessages to retrieve past user chats**
          Description: This ticket focuses on building the Lambda function responsible for retrieving previous messages based on a chat session ID. This Lambda will pull messages from DynamoDB and format them accordingly.
          (https://jiralevi9internship2025.atlassian.net/browse/SCRUM-25)

          - **ID: SCRUM-51 Enable pagination support in getMessages Lambda**
          Description: To improve performance and UX, implement pagination in the getMessages Lambda using limit and nextToken from DynamoDB queries.
          (https://jiralevi9internship2025.atlassian.net/browse/SCRUM-51)

          Let me know if you’d like ticket details or implementation notes!`,
        chat_id: this.chatId,
        timestamp: 1744008288
      },
      {
        user_message:"give me some tickets that are about JIRA",
        user_id : this.user_id,
        chat_message:`
        - **ID: SCRUM-48 Inicializar la función Lambda GetTickets para obtener tickets de Jira**
        Descripción: Desarrollar e implementar una función Lambda de AWS ({{GetTickets}}) para recuperar tickets de Jira de una instancia de Jira especificada a través de la API REST de Jira.
        (https://jiralevi9internship2025.atlassian.net/browse/SCRUM-48)

      //   - **ID: SCRUM-49 Reenviar la entrada del usuario a la función Lambda retrieveUserInput a través de una solicitud HTTP**
      //   Descripción: Como usuario, quiero enviar mi entrada (como un mensaje o datos) desde el frontend a una función Lambda de AWS a través de una solicitud HTTP, para que la función Lambda pueda procesar la entrada y devolver la respuesta adecuada que se mostrará en la interfaz de usuario.
      //   (https://jiralevi9internship2025.atlassian.net/browse/SCRUM-49)`,
      //   chat_id : this.chatId,
      //   timestamp:1744008299,
      // }
      // ]
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

  // Function to handle form submission
  onSubmit() {
    if (this.isSameAsLastPrompt()) {
      alert('Your input is the same as the last prompt. Please enter something different.');
      return;
    }
  
    const userMsg = this.userInput;
    this.userInput = "";
    this.thinking = true;
    
    const currentTime = new Date().toLocaleTimeString();
    const responseIndex = this.chatPairs.length;
  
    console.log("Chat Pairs before update: ", this.chatPairs);
  
    this.chatPairs.push({
      user: userMsg,
      bot: "", 
      timestamp: currentTime
    });
  
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
        formattedChatHistory = [];
      }
    }

    this.chatService.recieveUserInput({ message: userMsg }, formattedChatHistory).subscribe(res => {
      const parsedResponse = this.mdComp.convertMarkdownToHTML(res.response);
      this.newValue = parsedResponse;
      console.log("Parsed Response: ", parsedResponse);
    
      if (this.chatPairs[responseIndex]) {
        this.chatPairs[responseIndex].user = userMsg;
        this.chatPairs[responseIndex].bot = this.newValue;
        this.chatPairs[responseIndex].timestamp = new Date().toLocaleTimeString();
    
        console.log("Updated Chat Pairs after bot response: ", this.chatPairs);

        // ovde treba da se salje POST request do DINAMO-DB-a-------------------------------------------------
        this.chatService.postNewChatMessage(this.user_id, this.chatId, userMsg, parsedResponse).subscribe({
          next: (response) => {
            console.log('Message successfully saved to DynamoDB:', response);
            alert("Data successfuly saved")
          },
          error: (err) => {
            console.error('Failed to save message to DynamoDB:', err);
            // alert("Data is not successfuly saved"+ err)
          }
        });

        this.saveChatHistoryLocally();
    
        this.simulateTyping(parsedResponse, responseIndex);
      }
    
      console.log("Updated newValue after response: ", this.newValue);
    });
  }

  simulateTyping(response: string, responseIndex: number) {
    let words = response.split(' ');
    let currentWords = [];
    let index = 0;
    const wordsPerBatch = 5;
    const typingSpeed = 300;
  
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
    // Reset the height of the input element
    
    inputElement.style.height = 'auto';

    // Set the height to match the scrollHeight (to simulate expansion)
    inputElement.style.height = `${inputElement.scrollHeight}px`;

    // Ensure the height doesn't grow indefinitely, e.g., setting max-height
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
