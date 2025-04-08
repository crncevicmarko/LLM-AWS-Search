import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChatBotPageComponent } from './chat-bot-page.component';

describe('ChatBotPageComponent', () => {
  let component: ChatBotPageComponent;
  let fixture: ComponentFixture<ChatBotPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatBotPageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChatBotPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
