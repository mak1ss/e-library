# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Services at a Glance

| Service | Stack | Port | Storage |
|---|---|---|---|
| `apiGateway` | Spring Cloud Gateway | 9000 | — |
| `bookService` | Spring Boot 3 / JPA | 8080 | MySQL |
| `reviewService` | Spring Boot 3 / MongoDB | 8081 | MongoDB |
| `recommenderService` | FastAPI (Python) | 8082 | — |
| `book-bazaar` | Angular 20 | 4200 | — |

## Running the Stack

```bash
# Start all infrastructure + services
docker-compose up -d

# Production build (builds JARs/images first)
docker-compose -f docker-compose.prod.yml up -d
```

Infrastructure brought up by Docker: MySQL (3307), Keycloak (8181), MongoDB (27018), Kafka (9092), Schema Registry (8085), Kafka UI (8083), Prometheus (9090), Grafana (3000), Mailhog (8025).

## Build & Test Commands

**Java services** (run from each service directory):
```bash
mvn clean package -DskipTests   # build JAR
mvn test                         # run tests
mvn test -Dtest=MyTestClass      # run a single test class
```
Spring profiles: `dev` (default) and `prod`. Backend services read profile-specific config from `src/main/resources/application-dev.yml` / `application-prod.yml`.

**Angular frontend** (`book-bazaar/`):
```bash
npm start       # dev server at localhost:4200
npm run build   # production build
npm test        # Karma/Jasmine unit tests
```

**Python recommender** (`recommenderService/`):
```bash
pip install -r requirements.txt
python main.py
```

## Architecture

### Request Flow
Browser → Angular (4200) → **API Gateway** (9000) → `book-service` or `review-service`

The gateway validates JWT tokens issued by Keycloak and relays them to backend services via a token relay filter. Service-to-service calls use OpenFeign clients with client-credentials flow.

### Async Scoring Pipeline (Kafka)
1. `reviewService` publishes a `ReviewScoringRequest` (Avro) to `review-scoring-requests` after review **create** or text **update**.
2. `recommenderService` consumes it, runs cosine similarity with `all-MiniLM-L6-v2`, and publishes a `ReviewScoringResult` to `review-scoring-results`.
3. `reviewService` (`ReviewScoringResultListener`) consumes the result and persists it into `Review.scoringResult`.

Avro schemas live in each service's `src/main/resources/avro/`. The `avro-maven-plugin` generates Java POJOs at `generate-sources` phase.

### Key Patterns

**AbstractController / AbstractService** — all CRUD controllers and services extend base classes that provide pagination, soft-delete (archival via `archived` flag), and lifecycle hooks (`beforeCreate`, `afterCreate`, `beforeUpdate`, `beforeDelete`, `afterDelete`). Prefer adding logic in these hooks rather than overriding the full CRUD method.

**Filtering** — query string filters use the syntax `property:value` / `property!=value` / `property_=value` (contains). Multi-value OR uses `||`. Parsed by a `SearchCriteria` / `FilterableProperty` spec builder in each service.

**DTOs** — each entity has a `{Entity}Request` (input) and `{Entity}Response` (output) class; conversion goes through a `Mapper<Entity, Response, Request>` injected by the controller base class.

**Review metrics** — `ReviewMetricsService` keeps denormalised rating aggregates on the book side; it is called on every review create/update/delete.

### Auth
Keycloak realm `e-library` issues JWTs. Roles: `USER`, `ADMIN`. The gateway and each service are configured as OAuth2 resource servers pointing at `http://localhost:8181/realms/e-library`.

## Key File Locations

| What | Where |
|---|---|
| Gateway routes | `apiGateway/src/main/resources/application.yml` |
| Kafka topic names | `reviewService/src/main/resources/application-dev.yml` → `kafka.topics.*` |
| Avro schemas | `reviewService/src/main/resources/avro/` |
| Keycloak realm config | `infrastructure/keycloak/` |
| Prometheus config | `infrastructure/prometheus/prometheus-dev.yml` |
| MySQL init schema | `infrastructure/init.sql` |
| ML model config | `recommenderService/config.py` |
