import { ChangeDetectorRef, Component } from '@angular/core';
import { FormControl, FormGroup, FormsModule, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { CognitoUserPool, CognitoUserAttribute } from 'amazon-cognito-identity-js';
import { UserPostDTO } from '../models/userPostDTO.model';
import { environment } from '../../enviroments/enviroment';
import { HttpClient } from '@angular/common/http';
import { MaterialModule } from '../common/material.module';

@Component({
  selector: 'app-registration',
  imports: [MaterialModule],
  templateUrl: './registration.component.html',
  styleUrl: './registration.component.css'
})
export class RegistrationComponent {

  hide: boolean = true; // Hide/show password toggle

  createRegisterForm = new FormGroup({
    name: new FormControl('', Validators.required),
    surname: new FormControl('', Validators.required),
    username: new FormControl('', [Validators.required, Validators.email]) ,
    password: new FormControl('', Validators.required),
    confirmPassword: new FormControl('', Validators.required),
  });

  constructor(private cdr: ChangeDetectorRef, private router: Router, private snackBar: MatSnackBar,private httpClient: HttpClient) {}

  navigateToHome() {
    this.router.navigate(['home']);
  }

  
  register() {
    
    const user: UserPostDTO = {
      firstName: this.createRegisterForm.value.name,
      lastName: this.createRegisterForm.value.surname,
      username: this.createRegisterForm.value.username ?? '',
      password: this.createRegisterForm.value.password,
      email: this.createRegisterForm.value.username ?? ''
    };

    const attributeList: CognitoUserAttribute[] = [];

    if (user.email) {
      const emailAttribute = new CognitoUserAttribute({ Name: 'email', Value: user.email.toString() });
      attributeList.push(emailAttribute);
    }

    if (user.firstName) {
      const givenNameAttribute = new CognitoUserAttribute({ Name: 'given_name', Value: user.firstName });
      attributeList.push(givenNameAttribute);
    }

    if (user.lastName) {
      const familyNameAttribute = new CognitoUserAttribute({ Name: 'family_name', Value: user.lastName });
      attributeList.push(familyNameAttribute);
    }


    const poolData = {
      UserPoolId: environment.userPoolId, 
      ClientId: environment.userPoolClientId 
    };
    const userPool = new CognitoUserPool(poolData);


    if(user.username && user.password){
      userPool.signUp(user.username, user.password, attributeList.length > 0 ? attributeList : [], [], (err, result) => {
        if (err) {
          console.error('Error occurred during registration:', err);
          this.openErrorSnackBar('Failed to register user. Please try again.');
          return;
        }
        console.log('User registered successfully:', result?.user);
        this.router.navigate(['verifyAccount',user.username])
      });
    }
   

  }

  openErrorSnackBar(message: string) {
    this.snackBar.open(message, 'Close', {
      duration: 5000,
      horizontalPosition: 'center',
      verticalPosition: 'bottom',
      panelClass: ['error-snackbar']
    });
  }

  get isFormValid(): boolean {
    return this.createRegisterForm.valid;
  }
}
