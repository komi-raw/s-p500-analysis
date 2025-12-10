CREATE TABLE price_data (
    company VARCHAR(20) NOT NULL,
    date    DATETIME NOT NULL,
    open    DECIMAL(10,4) NOT NULL,
    low     DECIMAL(10,4) NOT NULL,
    high    DECIMAL(10,4) NOT NULL,
    close   DECIMAL(10,4) NOT NULL,
    volume  BIGINT NOT NULL,
    PRIMARY KEY (company, date)
);
