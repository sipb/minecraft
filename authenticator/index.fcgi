#!/usr/bin/node
/**
 * Author: Alex Huang (alexh95@mit.edu)
 * Created: 4/4/2020
 */

var fcgi = require('node-fastcgi');

const express = require('express'),
      app = express(),
      appHTTP = express(), // supports serving unsecured public page
      http = fcgi.createServer(appHTTP),
      fs = require('fs'),
      util = require('util'),
      morgan = require('morgan');
      bodyParser = require('body-parser'),
      sql = require('mysql');

const config = JSON.parse(fs.readFileSync('config.json', "utf8"));
const log_file = fs.createWriteStream(__dirname + '/debug.log', {flags : 'w'}),
      log_stdout = process.stdout;

console.log = function(d) {
  log_file.write(util.format(d) + '\n');
  log_stdout.write(util.format(d) + '\n');
}


const con = sql.createConnection({
  host     : config.SQL_HOST,
  user     : config.SQL_USER_TEST,
  password : config.SQL_PASSWORD_TEST,
  database : config.SQL_DB_NAME_TEST
});

// Users route, interface for all user DB interactions
const users = require('./users.js')(con);

//app.use(morgan(config.LOG_LEVEL, {stream : log_file));
// serve HTML from views directory

appHTTP.use('/', express.static('views/public'));
//appHTTP.get('/', function (req, res) {
////
////socket.getPeerCertificate()
//    if ('SSL_CLIENT_S_DN_Email' in req.socket.params) {
//        res.send(req.socket.params.SSL_CLIENT_S_DN_Email);
//	console.log(req.socket.params.SSL_CLIENT_S_DN_Email);
//    } else {
//	console.log(req.socket.params);
//        res.send("no certificate found, please visit https://minecraft.scripts.mit.edu:444");
//    }
////   res.send(JSON.stringify(req.socket.params));//'Hello World');
//});

function requireKerberos(req, res, next) {
  if ('SSL_CLIENT_S_DN_Email' in req.socket.params) {
    next();
  } else {
    res.send("Please log in with your MIT certificate at https://minecraft.scripts.mit.edu:444");
  }
}

  
app.use(bodyParser.json());
// all client calls to /user will go to users module
//app.use('/users', users); 
//appHTTP.use('/users', users); 
appHTTP.use('/users', requireKerberos, express.static('views/private')); 

con.connect(function(err){
  if (err) throw err;
  console.log("Connected to DB");
});
// Ugly but keeps the connection persistent by avoiding idle
setInterval(function(){
  con.query('SELECT 1');
  consoel.log('refresh');
}, 10000);

con.on('error', function(err){
  console.log("Error is:", err);
  throw err;
});
http.listen();

//https.listen(config.HTTPS_PORT);
