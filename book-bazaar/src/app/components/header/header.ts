import { Component, inject, signal } from '@angular/core';
import {MatButton} from '@angular/material/button';
import {RouterLink} from '@angular/router';
import { KeycloakProfile } from 'keycloak-js';
import { MatIcon } from '@angular/material/icon';
import { MatMenuModule } from '@angular/material/menu';
import Keycloak from 'keycloak-js';
import { UserService } from '../../services/user/userService';

@Component({
  selector: 'app-header',
  imports: [
    MatButton,
    RouterLink,
    MatIcon,
    MatMenuModule
],
  templateUrl: './header.html',
  styleUrl: './header.css',
})
export class Header {
  protected userService = inject(UserService);
}

