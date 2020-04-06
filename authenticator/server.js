/**
 * Author: Alex Huang (alexh95@mit.edu)
 * Created: 4/4/2020
 */

const express = require('express'),
      app = express(),
      http = require('http').Server(app),
      bodyParser = require('body-parser'),
      users = require('./users.js')('stub');

app.use(express.static('views'));

http.listen(3020);
