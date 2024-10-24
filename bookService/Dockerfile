FROM maven:3.9.9-amazoncorretto-17 AS build

WORKDIR /app

COPY pom.xml .
COPY src ./src

RUN mvn clean package -DskipTests

FROM amazoncorretto:17.0.11

WORKDIR /bookService

EXPOSE 8080

COPY --from=build  ./app/target/bookService.jar .

CMD java -jar bookService.jar

