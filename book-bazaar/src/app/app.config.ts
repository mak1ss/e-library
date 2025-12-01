import { ApplicationConfig, inject, provideAppInitializer, provideBrowserGlobalErrorListeners, provideZonelessChangeDetection } from '@angular/core';
import { provideRouter, withViewTransitions } from '@angular/router';

import { routes } from './app.routes';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import {
  provideKeycloak,
  INCLUDE_BEARER_TOKEN_INTERCEPTOR_CONFIG,
  includeBearerTokenInterceptor,
  createInterceptorCondition
} from 'keycloak-angular';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZonelessChangeDetection(),
    provideRouter(routes, withViewTransitions()),

    provideHttpClient(withInterceptors([includeBearerTokenInterceptor])),

    provideKeycloak({
      config: {
        url: 'http://localhost:8181',
        realm: 'e-library',
        clientId: 'e-library-client'
      },
      initOptions: {
        // 'check-sso': перевіряє сесію тихо. Якщо юзер залогінений - пускає, ні - лишає анонімом.
        // 'login-required': відразу кидає на сторінку логіну (вам це НЕ підходить).
        onLoad: 'check-sso',
        silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
        checkLoginIframe: false // Вимикаємо, щоб уникнути проблем з cookies у сучасних браузерах
      },
      // Автоматично додавати токен (Bearer) до запитів
    }),
    {
      provide: INCLUDE_BEARER_TOKEN_INTERCEPTOR_CONFIG,
      useValue: [
        createInterceptorCondition({
          urlPattern: /^(http:\/\/localhost:9000|http:\/\/localhost:8080)(\/.*)?$/i, // Регулярка для ваших сервісів
          bearerPrefix: 'Bearer'
        }),
        // Можна додати інші умови, якщо є інші бекенди
      ]
    }
  ]
};
