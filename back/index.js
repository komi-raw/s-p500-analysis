const express = require("express");
const mysql = require("mysql");
const app = express();
const port = 8080;

const con = mysql.createConnection({
    host: "localhost",
    user: "root",
    password: "sp500_root",
    database: "sp500",
});

app.use(function (req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Methods", "GET, PUT, POST");
    res.header(
        "Access-Control-Allow-Headers",
        "Origin, X-Requested-With, Content-Type, Accept"
    );
    next();
});

app.get("/api/company/list", (req, res) => {
    con.query("select * from company_data;", function (err, result) {
        if (err) throw err;
        res.send(result);
    });
});

app.get("/api/company/info", (req, res) => {
    con.query(`select * from sp500_company_data where symbol = '${req.query.code}';`, function (err, result) {
        if (err) throw err;
        res.send(result);
    });
});

app.get("/api/price/list", (req, res) => {
    con.query(`select * from ${req.query.code};`, function (err, result) {
        if (err) throw err;
        res.send(result);
    });
});

con.connect(function (err) {
    if (err) throw err;
    console.log("Connected!");

    app.listen(port, () => {
        console.log(`Example app listening on port ${port}`);
    });
});
