function remove (id, callback) {
  // this example uses the "pg" library
  // more info here: https://github.com/brianc/node-postgres

  postgres('postgres://lqmajjneumpdqu:22b6a581f14464fde19ca05f058b346ac4c0ff8a89f5469eb00699e4cfc260a1@ec2-54-221-221-153.compute-1.amazonaws.com:5432/djurcf15epg12?ssl=true', function (err, client, done) {
    if (err) {
      console.log('could not connect to postgres db', err);
      return callback(err);
    }

    client.query('DELETE FROM advisors WHERE pk_id = $1', [id], function (err) {
      // NOTE: always call `done()` here to close
      // the connection to the database
      done();

      if (err) {
        return callback(err);
      }

      callback(null);
    });
  });

}
