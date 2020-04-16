#!/usr/bin/node
/**
 * Author: Alex Huang (alexh95@mit.edu)
 * Created: 4/4/2020
 */

var fcgi = require('node-fastcgi');

const express = require('express'),
      app = express(),
      appHTTP = express(), // supports serving unsecured public page
      fs = require('fs'),
//      http = fcgi.createServer(appHTTP),
      http = require('http'),
      https = require('https'),
      morgan = require('morgan');
      bodyParser = require('body-parser'),
      sql = require('mysql');

const config = JSON.parse(fs.readFileSync('config.json', "utf8"));

const con = sql.createConnection({
  host     : config.SQL_HOST,
  user     : config.SQL_USER_TEST,
  password : config.SQL_PASSWORD_TEST,
  database : config.SQL_DB_NAME_TEST
});

const credentials = {
  key: fs.readFileSync(config.PRIVATE_KEY, 'utf8'),
  cert: fs.readFileSync(config.CERT, 'utf8'),
  ca: fs.readFileSync(config.CA, 'utf8'),
  requestCert: true,
  rejectUnauthorized: true
};

const httpServer = http.createServer(appHTTP),
      httpsServer = https.createServer(credentials, app)

// Users route, interface for all user DB interactions
const users = require('./users.js')(con);

// the public page, no cert required
appHTTP.use(express.static('views/public'));

// the private page/form, requires cert and HTTPS
app.use(express.static('views/private'));
app.use(morgan(config.LOG_LEVEL));
// serve HTML from views directory
app.use(bodyParser.json());
// all client calls to /user will go to users module
app.use('/users', users); 

// handle errors, respond to client
app.use((err, req, res, next) => {
  if (err) {
    console.log(err);
    return res.sendStatus(500);
  }
  next();
});

con.connect(function(err){
  if (err) throw err;
  console.log("Connected to DB");
});
// Ugly but keeps the connection persistent by avoiding idle
setInterval(function(){
  con.query('SELECT 1');
}, 10000);

con.on('error', function(err){
  console.log("Error is:", err);
  throw err;
});

//http.listen();

httpServer.listen(
  config.HTTP_PORT, 
  console.log("Server started, accepting requests on port:", 
  config.HTTP_PORT)
);

httpsServer.listen(config.HTTPS_PORT);
