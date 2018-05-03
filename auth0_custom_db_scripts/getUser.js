function getByEmail (email, callback) {
  var conString = "postgres://lqmajjneumpdqu:22b6a581f14464fde19ca05f058b346ac4c0ff8a89f5469eb00699e4cfc260a1@ec2-54-221-221-153.compute-1.amazonaws.com:5432/djurcf15epg12?ssl=true";
  console.log('HELLO IN GET USER');
  console.log('Email in getUser: ' + email);
  postgres(conString, function (err, client, done) {
    if (err) {
      console.log('could not connect to postgres db', err);
      return callback(err);
    }

    var query = 'SELECT pk_id, email, email_verified, first_name, last_name ' +
      'FROM advisors WHERE email = $1';
    console.log('query: ' + query);
    client.query(query, [email], function (err, result) {
      // NOTE: always call `done()` here to close
      // the connection to the database
      done();

      if (err) {
        console.log('error executing query', err);
        return callback(err);
      }

      if (result.rows.length === 0) {
        return callback(null);
      }

      var user = result.rows[0];
      var profile = {
        user_id:     user.pk_id,
        email: user.email,
        email_verified: user.email_verified,
        firstName: user.first_name,
        lastName: user.last_name
      };
      
      console.log('END OF GET USER');
      callback(null, profile);
    });
  });
}