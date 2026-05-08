import { inject, Injectable, signal, computed } from '@angular/core';
import Keycloak from 'keycloak-js'; // Імпорт класу/типу
import { KeycloakProfile } from 'keycloak-js';

@Injectable({
  providedIn: 'root'
})
export class UserService {
  // Інжектимо інстанс Keycloak
  private keycloak = inject(Keycloak);

  private userProfileSignal = signal<KeycloakProfile | undefined | null>(null);
  
  // Використовуємо .authenticated для початкового стану
  // На момент створення сервісу Keycloak вже ініціалізований!
  isLoggedIn = signal<boolean>(!!this.keycloak.authenticated); 

  userProfile = this.userProfileSignal.asReadonly();

  avatarUrl = computed(() => {
    const token = this.keycloak.idTokenParsed as any;
    if (token && token.picture) {
      console.log(token.picture)
      return token.picture;
    }

    // 2. Якщо в токені немає, пробуємо через профіль (резервний варіант)
    const profile = this.userProfileSignal();
    if (!profile) return null;
    
    // Перевірка на attributes (безпечний доступ)
    const attrs = (profile as any).attributes;
    if (attrs && attrs.picture && attrs.picture.length > 0) {
      return attrs.picture[0];
    }
    
    return null;
  });

  userName = computed(() => {
    const p = this.userProfileSignal();
    return p ? `${p.firstName}` : '';
  });

  isAdmin = computed(() =>
    !!(this.keycloak.tokenParsed as any)?.realm_access?.roles?.includes('ROLE_ADMIN')
  );

  constructor() {
    // Якщо юзер залогінений - одразу вантажимо профіль
    if (this.isLoggedIn()) {
      this.loadProfile();
    }
  }

  private async loadProfile() {
    try {
      const profile = await this.keycloak.loadUserProfile();
      this.userProfileSignal.set(profile);
    } catch (e) {
      console.error('Error loading profile', e);
    }
  }

  login() {
    this.keycloak.login();
  }

  logout() {
    this.keycloak.logout();
  }

  register() {
    this.keycloak.register();
  }
}