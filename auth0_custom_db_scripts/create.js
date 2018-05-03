function create(user, callback) {
  //this example uses the "pg" library
  //more info here: https://github.com/brianc/node-postgres

  var conString = "postgres://lqmajjneumpdqu:22b6a581f14464fde19ca05f058b346ac4c0ff8a89f5469eb00699e4cfc260a1@ec2-54-221-221-153.compute-1.amazonaws.com:5432/djurcf15epg12?ssl=true";
  console.log("Email is: " + user.email);
  postgres(conString, function (err, client, done) {
    if (err) {
      console.log('could not connect to postgres db', err);
      return callback(err);
    }
    bcrypt.hash(user.password, 10, function (err, hashedPassword) {
      var new_pk_id = require('node-uuid').v4().toString();
      var query = 'INSERT INTO advisors(pk_id, email, password, email_verified, completed_account_setup) VALUES ($1, $2, $3, $4, $5)';
      client.query(query, [new_pk_id, user.email, hashedPassword, false, false], function (err, result) {
        // NOTE: always call `done()` here to close
        // the connection to the database
        done();
        if (err) {
          console.log('error executing query', err);
          return callback(err);
        }
        if (result.rows.length === 0) {
          return callback();
        }
        callback(null);
      });
    });
  });
}
