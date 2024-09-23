FROM amazoncorretto:17.0.11

RUN mkdir /reviewService

COPY target/reviewService.jar /reviewService/reviewService.jar

EXPOSE 8081

WORKDIR /reviewService

CMD java -jar reviewService.jar

