import { bootstrapApplication } from '@angular/platform-browser';
import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { appConfig } from './app/app.config';
import { AppModule } from './app/app.module';

(globalThis as any).global = globalThis;

platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(err => console.error(err));
