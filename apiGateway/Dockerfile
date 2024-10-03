FROM maven:3.9.9-amazoncorretto-17 AS build

WORKDIR /app

COPY pom.xml .
COPY src ./src

RUN mvn clean package -DskipTests

FROM amazoncorretto:17.0.11

EXPOSE 8080

WORKDIR /app

COPY --from=build ./app/target/apiGateway.jar .

CMD java -jar apiGateway.jar

