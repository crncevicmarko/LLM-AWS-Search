import { Component, ElementRef, ViewChild } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { environment } from '../../enviroments/enviroment';
import { CognitoUserPool, CognitoUser, AuthenticationDetails } from 'amazon-cognito-identity-js';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MaterialModule } from '../common/material.module';
@Component({
  selector: 'app-login',
  imports: [MaterialModule],
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
    private router: Router
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
              const idToken = session.getIdToken().getJwtToken();
              console.log('idToken:', idToken);

              localStorage.setItem('idToken', idToken);
              console.log('Stored idToken in localStorage:', idToken);
              const username = session.getIdToken().payload['email'];//dobavljamo email tj username iz id  tokena
              localStorage.setItem('username',username)
              console.log('Username : ',username)
              this.router.navigate(["/chat"])
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
  //dobijamo korisnicko ime iz tokena
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

      // Traženje korisničkog imena (username)
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
