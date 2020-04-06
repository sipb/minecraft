/**
 * Module that provides an interface to our SQL DB, which keeps track of user
 * state
 */

module.exports = (function(sql) {

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

});
