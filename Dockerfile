FROM mysql:8.0-debian

RUN apt-get update && apt-get install -y python3 python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV MYSQL_ROOT_PASSWORD=sp500_root
ENV MYSQL_DATABASE=sp500
ENV MYSQL_USER=sp500_main
ENV MYSQL_PASSWORD=sp500_main

COPY ./stocks /stocks/

EXPOSE 3306
