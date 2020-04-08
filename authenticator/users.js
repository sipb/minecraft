/**
 * Module that provides an interface to our SQL DB, which keeps track of user
 * state and an API for clients 
 *
 * Requires SQL connection object to be passed in
 */

module.exports = (function(con) {
  const router = require('express').Router(),
  moment = require('moment');

  /*
   * Gets user's DB record by kerberos
   * Returns a object with status of query and SQL record object, if found
   */
  function getRecordByKerberos(kerberos){}

  /*
   * Gets user's Minecraft UUID from DB
   * Returns an object with status of query and UUID, if found
   */
  function getUUIDByKerberos(kerberos){}

  /*
   * Gets user's current Minecraft username 
   * Returns an object with status of query and MC username, if found
   */
  function getUserNameByUUID(uuid) {}

  /*
   * Insert a record into database
   */
  function insertRecord(kerberos, uuid, req, res){
    con.query(
      'INSERT INTO `minecraft_users` SET kerberos= ?, uuid = ?, time = ?',
      [kerberos, uuid, '0'],
      function(err, results, field) {
        // TODO think about whether this is correct err handling behavior
        if (err) {
          if (err.code === 'ER_DUP_ENTRY') {
            console.log("UUID is already in DB");
          } else {
            console.log(err);
            throw err;
          }
          res.sendStatus(400);
        } else { 
          console.log('Successfully added record for', kerberos);
        }
      }
    );
  }

  /*
   * Update a record in the database
   *
   * Assumes that only one record exists in the DB
   */
  function updateRecord(kerberos, uuid, req, res){
    con.query(
      'UPDATE `minecraft_users` SET uuid = ?, time = ? WHERE kerberos = ?',
      [uuid, '0', kerberos],
      function(err, results, field) {
        // TODO think about whether this is correct err handling behavior
        if (err) {
          if (err.code === 'ER_DUP_ENTRY') {
            console.log("UUID is already in DB");
          } else {
            console.log(err);
            throw err;
          }
          res.sendStatus(400);
        } else { 
          console.log('Successfully updated record for', kerberos);
          res.sendStatus(200);
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
        } else {
          if (results.length) {
            //send record back in json
            console.log(JSON.stringify(results[0]));
            res.sendStatus(200);
          } else {
            // no result
            res.sendStatus(404);
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
        uuid = req.body.uuid;
    //TODO fetch UUID
    console.log(req.body);
    //TODO sanitize user input
    con.query(
      'SELECT 1 FROM  `minecraft_users` WHERE kerberos = ?',
      kerberos,
      function(err, results, field) {
        // TODO handle error
        if(err) {
        }
        console.log(results);
        if (results.length) {
          // Update
          console.log("Updating record for:", kerberos);
          updateRecord(kerberos, uuid, req, res);
        } else {
          // Insert
          console.log("Adding record for:", kerberos);
          insertRecord(kerberos, uuid, req, res);
        }
      }
    );
  });

  return router;
});
