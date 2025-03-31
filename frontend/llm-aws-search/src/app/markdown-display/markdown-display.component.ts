import { Component, Injectable, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../enviroments/enviroment';
import { marked } from 'marked';

@Component({
  selector: 'app-markdown-display',
  templateUrl: './markdown-display.component.html',
  styleUrls: ['./markdown-display.component.css'],
  standalone:false,

})
@Injectable({
  providedIn: 'root'
})
export class MarkdownDisplayComponent implements OnInit {
  markdownContent: string = '';  // Holds the Markdown content
  htmlContent: string = '';  // Holds the HTML after conversion

  constructor(private http: HttpClient) {}

  ngOnInit(): void {
  }

  // Convert Markdown content to HTML using the marked library
  convertMarkdownToHTML(text :string) {
    this.htmlContent = marked(text) as string;
    return marked(text) as string;
  }
}
