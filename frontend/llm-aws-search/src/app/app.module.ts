import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppComponent } from './app.component';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

@NgModule({
  declarations: [
    AppComponent,  // Declare your components here
  ],
  imports: [
    BrowserModule,  // Import essential modules here
    HttpClientModule,  // Import HttpClientModule to enable HTTP requests
    FormsModule,
    RouterModule
  ],
  providers: [],
  bootstrap: [AppComponent]  // Specify your root component
})
export class AppModule { }
