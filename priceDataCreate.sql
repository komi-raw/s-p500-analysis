CREATE TABLE price_data (
    companyId INT NOT NULL,
    date    DATETIME NOT NULL,
    open    DECIMAL(10,4) NOT NULL,
    low     DECIMAL(10,4) NOT NULL,
    high    DECIMAL(10,4) NOT NULL,
    close   DECIMAL(10,4) NOT NULL,
    volume  BIGINT NOT NULL,
    PRIMARY KEY (companyId, date),
    FOREIGN KEY(companyId) REFERENCES company_data(companyIdx)
);

CREATE TABLE company_data (
    companyIdx INT NOT NULL AUTO_INCREMENT,
    code    CHAR(10) NOT NULL,
    name    VARCHAR(100),
    PRIMARY KEY (companyIdx)
);
