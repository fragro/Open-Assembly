
(function() {


    var fs = require('fs');
    var ron = require('ron');

    try{
      //dotcloud environment parametes for hooking into our own redis server
      var env = JSON.parse(fs.readFileSync('/home/dotcloud/environment.json', 'utf-8'));
      var port = env.DOTCLOUD_CACHE_REDIS_PORT;
      var host = env.DOTCLOUD_CACHE_REDIS_HOST;
     }
    catch(e){
      //running on dev server
      var port = 6379;
      var host = 'localhost';
    }

      // Client connection
    client = ron({
        port: port,
        host: host,
        name: 'auth'
    });

    // Schema definition
    var Users = client.get('users');
    Users.property('id', {identifier: true});
    Users.property('username', {unique: true});
    Users.property('online', {index: true, type: 'int', temporal: true});

    module.exports.init = function(id, username, online) {

      var u = Users.get({id: id}, {});
      if(u === null){
        // Record manipulation
        Users.create(
            {id: id, username: username, online: online},
            function(err, user){
                console.log(err, user.id);
            }
        );
      }
      return u;
    };

}());