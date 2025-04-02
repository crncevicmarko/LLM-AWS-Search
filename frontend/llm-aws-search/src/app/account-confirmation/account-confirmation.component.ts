
import { MaterialModule } from '../common/material.module';

import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { CognitoUser, CognitoUserPool } from 'amazon-cognito-identity-js';
import { ActivatedRoute } from '@angular/router';
import {MatIconModule} from '@angular/material/icon';
import {MatInputModule} from '@angular/material/input';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatButtonModule} from '@angular/material/button';
import { Router } from '@angular/router';
import { ViewChild, ElementRef } from '@angular/core';
import { environment } from '../../enviroments/enviroment';

import { ReactiveFormsModule } from '@angular/forms';

import { MatSnackBarModule } from '@angular/material/snack-bar';
@Component({
  selector: 'app-account-confirmation',
  imports: [MaterialModule,ReactiveFormsModule,CommonModule],
  templateUrl: './account-confirmation.component.html',
  styleUrl: './account-confirmation.component.css',

})
export class AccountConfirmationComponent implements OnInit {

  confirmationForm: FormGroup;
  userPool = new CognitoUserPool({
    UserPoolId: environment.userPoolId, 
    ClientId: environment.userPoolClientId
  });

  constructor(private fb: FormBuilder, private snackBar: MatSnackBar, private route: ActivatedRoute) {
    this.confirmationForm = this.fb.group({
      confirmationCode: ['', Validators.required]
    });
  }

  ngOnInit() {
    this.confirmationForm = this.fb.group({
      confirmationCode: ['', Validators.required] // Polje za unos potvrdnog koda
    });

    // Učitavanje korisničkog imena iz parametara rute
    this.route.params.subscribe(params => {
      const username = params['username'];
      if (username) {
        // Možete ovde raditi sa korisničkim imenom, na primer prikazivanje ili čišćenje forme
      }
    });
  }

  confirmAccount() {
    const username = this.route.snapshot.params['username']; // Dobijanje korisničkog imena iz snapshot-a rute

    const user = new CognitoUser({
      Username: username,
      Pool: this.userPool
    });

    user.confirmRegistration(this.confirmationForm.value.confirmationCode, true, (err, result) => {
      if (err) {
        console.error('Error confirming account:', err);
        this.snackBar.open('Failed to confirm account. Please try again.', 'Close', { duration: 3000 });
      } else {
        console.log('Account confirmed successfully:', result);
        this.snackBar.open('Account confirmed successfully.', 'Close', { duration: 3000 });
        // Možete dodati redirekciju na stranicu nakon uspešne potvrde naloga
      }
    });
  }

}
