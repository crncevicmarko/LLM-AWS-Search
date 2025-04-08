import { Injectable } from '@angular/core';
import {
  CanActivate,
  ActivatedRouteSnapshot,
  RouterStateSnapshot,
  Router,
} from '@angular/router';
import { AuthService } from '../services/auth.service';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AuthGuard implements CanActivate {
  constructor(private router: Router, private authService: AuthService) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): boolean {
    const token = this.authService.getAccessTokenFromLocalStorage(); 

    if (token) {
      if (route.routeConfig?.path === 'login' || route.routeConfig?.path === 'register') {
        this.router.navigate(['chat']);
        return false;
      }
    }else{
      if(route.routeConfig?.path === 'login' || route.routeConfig?.path === 'register') return true;
      this.router.navigate(['login']);
      return false;
    }
    return true;
  }
}
