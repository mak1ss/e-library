FROM amazoncorretto:17.0.11

RUN mkdir /bookService

COPY target/bookService.jar /bookService/bookService.jar

EXPOSE 8080

WORKDIR /bookService

CMD java -jar bookService.jar

