function login(email, password, callback) {
  //this example uses the "pg" library
  //more info here: https://github.com/brianc/node-postgres

  var conString = "postgres://lqmajjneumpdqu:22b6a581f14464fde19ca05f058b346ac4c0ff8a89f5469eb00699e4cfc260a1@ec2-54-221-221-153.compute-1.amazonaws.com:5432/djurcf15epg12?ssl=true";
  postgres(conString, function (err, client, done) {
    if (err) {
      console.log('could not connect to postgres db', err);
      return callback(err);
    }

    var query = 'SELECT pk_id, email, email_verified, password, first_name, last_name ' +
      'FROM advisors WHERE email = $1';

    client.query(query, [email], function (err, result) {
      // NOTE: always call `done()` here to close
      // the connection to the database
      done();

      if (err) {
        console.log('error executing query', err);
        return callback(err);
      }

      if (result.rows.length === 0) {
        console.log("something went wrong?");
        return callback(new WrongUsernameOrPasswordError(email));
      }

      var user = result.rows[0];

      bcrypt.compare(password, user.password, function (err, isValid) {
        if (err) {
          callback(err);
        } else if (!isValid) {
          callback(new WrongUsernameOrPasswordError(email));
        } else {
          callback(null, {
            user_id: user.pk_id,
            email: user.email,
            email_verified: user.email_verified,
            firstName: user.first_name,
            lastName: user.last_name            
          });
        }
      });
    });
  });
}
