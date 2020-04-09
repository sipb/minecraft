/**
 * Module that provides an interface to our SQL DB, which keeps track of user
 * state and an API for clients 
 *
 * Requires SQL connection object to be passed in
 * Requires kerberos to be valid since it should be obtained via signed cert
 *
 * Special thanks to Diane Zhou for delivering me food while I wrote this
 */

module.exports = (function(con) {
  const router = require('express').Router(),
        fetch = require('node-fetch'),
        moment = require('moment'),
        colors = require('colors');

  const HTTP_GOOD = 200,
        HTTP_BAD_REQUEST = 400,
        HTTP_NOT_FOUND = 404,
        HTTP_SERVER_ERROR = 500;

  /*
   * Insert a record into database asynchronusly
   */
  function insertRecord(kerberos, uuid, res){
    con.query(
      'INSERT INTO `minecraft_users` SET kerberos= ?, uuid = ?, time = ?',
      [kerberos, uuid, moment().unix()],
      function(err, results, field) {
        if (err) {
          if (err.code === 'ER_DUP_ENTRY') {
            console.error(colors.red("UUID", uuid, "already exists in DB"));
            res.sendStatus(HTTP_BAD_REQUEST);
          } else {
            console.error(colors.red(err));
            res.sendStatus(HTTP_SERVER_ERROR);
          }
        } else { 
          console.log('Successfully added record for', kerberos);
          res.sendStatus(HTTP_GOOD);
        }
      }
    );
  }

  /*
   * API call to playerDB to get player UUID
   *
   * returns a promise with the response JSON
   */
  function fetchUUID(username) {
    return fetch('https://playerdb.co/api/player/minecraft/' + username)
      .then(res => res.json());
  }

  /*
   * Update a record in the database asynchronously
   *
   * Assumes that only one record exists in the DB
   */
  function updateRecord(kerberos, uuid, res){
    con.query(
      'UPDATE `minecraft_users` SET uuid = ?, time = ? WHERE kerberos = ?',
      [uuid, moment().unix(), kerberos],
      function(err, results, field) {
        // TODO think about whether this is correct err handling behavior
        if (err) {
          if (err.code === 'ER_DUP_ENTRY') {
            console.error(colors.red("UUID", uuid, "exists in DB"));
            res.sendStatus(HTTP_BAD_REQUEST);
          } else {
            console.error(colors.red(err));
            res.sendStatus(HTTP_SERVER_ERROR);
          }
        } else { 
          console.log('Successfully updated record for', kerberos);
          res.sendStatus(HTTP_GOOD);
        }
      }
    );
  }

  /*
   * Route for clients to GET their UUID
   */
  router.post('/find_record', function(req, res){
    let kerberos = req.body.kerberos;
    console.log("Finding record for", kerberos);
    con.query(
      'SELECT uuid, time FROM  `minecraft_users` WHERE kerberos = ?',
      kerberos, 
      function(err, results, fields) {
        if(err) {
          res.send(HTTP_SERVER_ERROR);
        } else {
          if (results.length) {
            //send record back in json
            let record = JSON.stringify(results[0]);
            res.send(record);
          } else {
            // no result
            res.sendStatus(HTTP_NOT_FOUND);
          }
        }

      }
    );
  });

  /*
   * Route for clients to POST permission requests
   */
  router.post('/add_record', function(req, res){
    let kerberos = req.body.kerberos,
        username = encodeURI(req.body.username); //encode to prevent injection

    console.log("Got request to add record:", req.body);
    //fetch UUID
    console.log("Fetching UUID for", kerberos);
    fetchUUID(username).then(function(player_json){
      let fetch_status = player_json.success;
      if (fetch_status) {
        let uuid = player_json.data.player.id;
        console.log(colors.green(
          "Found UUID", uuid, "for", kerberos)
        );
        // DB operations
        con.query(
          'SELECT 1 FROM  `minecraft_users` WHERE kerberos = ?',
          kerberos,
          function(err, results, field) {
            if(err) {
              res.sendStatus(HTTP_SERVER_ERROR);
            } else {
              if (results.length) {
                // Update
                console.log("Updating record for:", kerberos);
                updateRecord(kerberos, uuid, res);
              } else {
                // Insert
                console.log("Adding record for:", kerberos);
                insertRecord(kerberos, uuid, res);
              }
            }
          }
        );
      } else {
        // Bad MC username
        console.log(colors.yellow(
          "Unable to find minecraft username:", username, "for", kerberos
        ));
        res.sendStatus(HTTP_BAD_REQUEST);
      }
    })
  });

  return router;
});
