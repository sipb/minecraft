#!/usr/bin/node
/**
 * Author: Alex Huang (alexh95@mit.edu)
 * Created: 4/4/2020
 */

var fcgi = require('node-fastcgi');

const express = require('express'),
      app = express(), // supports serving unsecured public page
      fs = require('fs'),
      http = fcgi.createServer(app),
      util = require('util'),
      morgan = require('morgan');
      bodyParser = require('body-parser'),
      sql = require('mysql');

const config = JSON.parse(fs.readFileSync('config.json', "utf8"));

// log to a file
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
app.use(bodyParser.json());
// anyone can see the public director
app.use('/', express.static('views/public'));

// middleware to prevent people without valid MIT certs to app
function requireKerberos(req, res, next) {
  if ('SSL_CLIENT_S_DN_Email' in req.socket.params) {
    next();
  } else {
    res.send("Please log in with your MIT certificate at" +
      "https://minecraft.scripts.mit.edu:444");
  }
}
  
app.use('/users', requireKerberos, express.static('views/private')); 

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
  consoel.log('refresh');
}, 10000);

con.on('error', function(err){
  console.log("Error is:", err);
  throw err;
});


http.listen();
