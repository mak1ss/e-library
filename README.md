# 📚 E-Library 📚

E-Library is a microservice-based application for managing books and their reviews. 📖 The project is built with Spring Boot, uses an API Gateway for request routing, and ensures security through Keycloak. 🔐

## ⚙️ Architecture ⚙️

The project consists of the following core microservices:

1. **Book Service** (Spring Boot + MySQL) 📘
   - API for books, authors, publishers, genres, and categories.  
   - Filtering via JPA Specification.  
   - Secured and public endpoints (see "Security" section).  

2. **Review Service** (Spring Boot + MongoDB) 📝
   - API for book reviews.  
   - Filtering reviews via query parameters.  
   - Book review metrics.  

3. **API Gateway** (Spring Cloud API Gateway) 🚀
   - Routes `review-service/` and `book-service/` requests to corresponding services.  
   - Uses OAuth2 (Keycloak) for authentication and authorization.  
   - Passes JWT tokens between services for role validation.  
   - Supports integration via registered Keycloak clients.  

## 🛠️ Setup & Configuration 🛠️

- The local environment runs with `docker-compose.yml`.  
- The production environment uses `docker-compose.prod.yml`, which extends and overrides base configurations.  
- Each microservice has separate configuration files:  
  - `application-dev.yml` (local development)  
  - `application-prod.yml` (production)  

## 🔒 Security 🔒

### 🏷️ User Roles 🏷️
- **USER** — regular user.  
- **ADMIN** — administrator with add/edit privileges.  

### 🔑 API Access 🔑

#### **Book Service**
- Requires authentication even for public `GET` requests due to Keycloak validation at the gateway level. For such requests, `client credentials flow` can be used if registered clients with this flow exist in Keycloak.
- Public access:
  - `GET /api/books/**`
  - `GET /api/authors/**`
  - `GET /api/publishers/**`
  - `GET /api/genres/**`
  - `GET /api/categories/**`
- ADMIN-only access:
  - `POST/PUT/DELETE /api/books/**`
  - `POST/PUT/DELETE /api/authors/**`
  - `POST/PUT/DELETE /api/publishers/**`
  - `POST/PUT/DELETE /api/genres/**`
  - `POST/PUT/DELETE /api/categories/**`

#### **Review Service**
- Requires authentication even for public `GET` requests due to Keycloak validation at the gateway level. For such requests, `client credentials flow` can be used if registered clients with this flow exist in Keycloak.
- Public access:
  - `GET /api/reviews/**`
  - `GET /api/review-metrics/**`
- USER & ADMIN access:
  - `POST/PUT/DELETE /api/reviews/**`

- Tokens are verified through Keycloak. Refresh and revocation are handled via the Keycloak API. 🔄

## 🔗 API & Integration 🔗
- All microservices have OpenAPI/Swagger documentation. 📜
- API Gateway aggregates the documentation from all services. 📌
- Only registered users can leave reviews. 🏷️

## 📊 Monitoring & Logging 📊

- Uses Spring Boot Actuator & Prometheus for metrics collection. 📈
- Prometheus gathers and stores microservice metrics. 🗂️
- Grafana automatically loads dashboards from pre-configured settings. 📊
- No centralized logging (ELK, Loki). 🚫

## ⚡ CI/CD & Deployment ⚡

- **GitHub Actions** is used for CI: 🛠️
  - Each service has its own `.github/workflows` file. 📁
  - CI runs only when changes are made in the corresponding microservice. 🔄
  - Compilation, testing, and Docker image build are performed. 🏗️
- No automatic deployment (handled by the DevOps team). 🔧

