import { Component, ElementRef, ViewChild } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { environment } from '../../enviroments/enviroment';
import { CognitoUserPool, CognitoUser, AuthenticationDetails } from 'amazon-cognito-identity-js';
import { Router, RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../common/material.module';
import { AuthService } from '../services/auth.service';
@Component({
  selector: 'app-login',
  imports: [MaterialModule, RouterModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {
  hide: boolean = true;
  @ViewChild('usernameInput') usernameInput!: ElementRef;
  @ViewChild('passwordInput') passwordInput!: ElementRef;

  loginForm = new FormGroup({
    username: new FormControl(),
    password: new FormControl()
  });

  private userPoolData = {
    UserPoolId: environment.userPoolId,
    ClientId: environment.userPoolClientId
  };

  private userPool = new CognitoUserPool(this.userPoolData);

  constructor(
    private router: Router,
    private authService: AuthService
  ) {}

  login(): void {
    if (this.loginForm.valid) {
      const username = this.usernameInput.nativeElement.value;
      const password = this.passwordInput.nativeElement.value;

      const authenticationData = {
        Username: username,
        Password: password
      };

      const authenticationDetails = new AuthenticationDetails(authenticationData);

      const userData = {
        Username: authenticationData.Username,
        Pool: this.userPool
      };

      const cognitoUser = new CognitoUser(userData);

      cognitoUser.authenticateUser(authenticationDetails, {
        onSuccess: (result) => {
          console.log('Login successful:', result);

          cognitoUser.getSession((err:any, session:any) => {
            if (err) {
              console.error('Error getting session:', err);
              return;
            }

            if (session) {
              const accessToken = session.getAccessToken().getJwtToken();

              localStorage.setItem('accessToken', accessToken);
              
              const username = session.getAccessToken().payload['email'];
              localStorage.setItem('username',username);
              this.authService.logIn();
              this.router.navigate(["/chat"]);
            }
          });
        },
        onFailure: (err) => {
          console.error('Login failed:', err);
        }
      });
    }
  }

  register() {
    this.router.navigate(['register']);
  }
  getUsernameFromSub(sub: string) {
    const poolData = {
      UserPoolId: environment.userPoolId,
      ClientId: environment.userPoolClientId
    };

    const userPool = new CognitoUserPool(poolData);
    const userData = {
      Username: sub,
      Pool: userPool
    };

    const cognitoUser = new CognitoUser(userData);
    cognitoUser.getUserAttributes((err, attributes) => {
      if (err) {
        console.error('Error fetching user attributes:', err);
        return;
      }

      if (attributes) {
        for (let attribute of attributes) {
          if (attribute.getName() === 'sub') {
            console.log('Username:', attribute.getValue());
            break;
          }
        }
      }
    });
  }
}
