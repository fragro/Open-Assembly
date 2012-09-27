var fs = require('fs');
var app = require('express').createServer(),
    redis = require('socket.io/node_modules/redis'),
    io = require('socket.io').listen(app);


//CHAT SOCKETIO CODE
// usernames which are currently connected
var users = {};
var rooms = {};
//should probably transfer this to redis instead of the local nodejs server in case of reboot
redis.debug_mode = true;

process.on('SIGTERM', function () {
  console.log('Got SIGTERM, exiting...');
  process.exit(0);
});

try{
  //dotcloud environment parametes for hooking into our own redis server
  var env = JSON.parse(fs.readFileSync('/home/dotcloud/environment.json', 'utf-8'));
  var port = env['DOTCLOUD_CACHE_REDIS_PORT'];
  var host = env['DOTCLOUD_CACHE_REDIS_HOST'];
  var nodeport = 42801; 
  //connect to redis
  var sub = redis.createClient(port, host);
  sub.auth(env['DOTCLOUD_CACHE_REDIS_PASSWORD'])
  var store = redis.createClient(port, host); 
  store.auth(env['DOTCLOUD_CACHE_REDIS_PASSWORD'])
  var p2p = redis.createClient(port, host);
  p2p.auth(env['DOTCLOUD_CACHE_REDIS_PASSWORD'])

 }
catch(e){
  //running on dev server
  var nodeport = 8080;
  var port = 6379;
  var host = 'localhost';
  var sub = redis.createClient(port, host);
  var store = redis.createClient(port, host);
  var p2p = redis.createClient(port, host); 
}
// 


//var store = redis.createClient(port, host);
// pub.auth('pass', function(){console.log("adentro! pub")});
// sub.auth('pass', function(){console.log("adentro! sub")});
// store.auth('pass', function(){console.log("adentro! store")});

app.listen(nodeport);

//returns new_user, true if this user has joined this chat for the first time this session
function init_user(username, sessionid, socketid, room, type){
  if(room != null){
    var u1 = users[sessionid];
    var new_user = true;
    if(u1){
      console.log(u1);
      if(u1[type][room] == 1){
        new_user = false;
      }
      else{
        u1[type][room] = 1;
      }
    }
    else{
      users[sessionid] = {'username': username, 'socketid': socketid, 'sessionid': sessionid, 'chats': {}, 'p2p': {}};
      users[sessionid][type][room] = 1; 
    }
    return new_user;
  }
  else{
    users[sessionid] = {'username': username, 'socketid': socketid, 'sessionid': sessionid, 'chats': {}, 'p2p': {}};
  }
}

function init_room(room, username){

  var r1 = rooms[room];
  if(r1){
    rooms[room][username] = 1;
  }
  else{
    rooms[room] = {};
    rooms[room][username] = 1;
  }
}

//takes a user name and returns true if that user has an connected socket
function user_online(user){
  store.get(user, function (err, reply) {
        if(reply != null){
          return true;
          console.log('USER ONLINE');
          console.log(reply.toString());
        }
        else{
          return false;
        }
      });
}



function socket_throughput(user, message){
  console.log("client1 channel " + user + ": " + message);
      store.get(user, function (err, reply) {
        if(reply != null){
          //user is online
          console.log('reply from redis: ' + reply.toString());
          var sessionid = reply.toString();
          console.log(users[sessionid]['socketid']);
          io.sockets.socket(users[sessionid]['socketid']).emit('updateUI', message); 

        }
      });
}

////REDIS SUBSCRIPTION MESSAGES
//when redis sends us a message about a channel we are subscribed to: logic
sub.on("message", function (channel, message) {
    socket_throughput(channel, message);
});


//CHAT SERVER AND SOCKET BASED SUBSCRIPTIONS

io.sockets.on('connection', function (socket) {

  // when the client emits 'sendchat', this listens and executes
  socket.on('sendchat', function(data, room) {
    // we tell the client to execute 'updatechat' with 2 parameters
      try{
        io.sockets.to(room).emit('updatechat', users[socket.username]['username'], data, room, users[socket.username]['sessionid']);
      }
      catch(err){
        console.log(err);
        io.sockets.socket(socket.id).emit('updatechat', 'SERVER', 'Still connecting. Wait a few seconds please.', room);
      }
  });

  // when the client emits 'sendchat', this listens and executes
  socket.on('sendP2P', function(data, room) {
    // we tell the client to execute 'updatechat' with 2 parameters
      store.get(users[socket.username]['username'] + room, function (err, reply) {
        console.log(reply.toString());
        console.log(room);
        io.sockets.to(room).emit('updateP2P', users[socket.username]['username'], data, room, users[socket.username]['sessionid'], reply.toString());
      });


  });

  //when the user subscribes to dynamic events through socket.io, register the redis SUB
  socket.on('subscribe', function(username, sessionid){
    console.log('subscribed to ' + username);
    //initialize user so we can responsd to the right socket for real-time events
    init_user(username, sessionid, socket.id, null);
    sub.subscribe(username);

    store.set(username, sessionid);
    //store.expire(username, -1)
  });

  //when the user subscribes to dynamic events through socket.io, register the redis SUB
  socket.on('subscribeP2P', function(username, key, sessionid, url){
    console.log('subscribed to ' + key);
    //initialize user so we can responsd to the right socket for real-time events
    socket.join(key);
    //store user image url for future callbacks to server
    store.set(username + key, url);
    new_user = init_user(username, sessionid, socket.id, key, 'p2p');
    io.sockets.to(key).emit('updateP2P', 'SERVER', ' ', key, sessionid, 'ONLINE');


    //store.expire(username, -1)
  });

  //chekc if the user is currently subscribed to nodejs
  socket.on('is_online', function(username, key, sessionid){
    is_online = user_online(username)
    if(is_online){
      io.sockets.socket(socket.id).emit('updateP2P', 'SERVER', ' ', key, sessionid, 'ONLINE');
    }

  });

  // when the client emits 'adduser', this listens and executes
  socket.on('adduser', function(username, sessionid, room){
    console.log('adding user' + sessionid);
    socket.set('room', room, function() { console.log('room ' + room + ' saved'); } );
    socket.join(room);
    // we store the username in the socket session for this client
    socket.username = sessionid;
    // add the client's username to the global list
    new_user = init_user(username, sessionid, socket.id, room, 'chats');
    init_room(room, username);
    if(new_user){
      // echo globally (all clients in that room) that a person has connected
      socket.broadcast.to(room).emit('updatechat', 'SERVER', username + ' has connected', room, sessionid, 'connect' );
    }
    socket.to(room).emit('updatechat', 'SERVER', 'you have connected', room, sessionid);
    // update the list of users in chat, client-side
    io.sockets.to(room).emit('updateusers', rooms[room], room);
  });

  // when the user disconnects.. perform this
  socket.on('disconnect', function(){
    // remove the username from global usernames list
    user = users[socket.username]
    if(user){
      chatlist = user['chats']
      p2plist = user['p2p']

      // update list of users in chat, client-side
      for(var room in chatlist){
        //first check to 
        try{
          delete rooms[room][users[socket.username]['username']]
          io.sockets.to(room).emit('updateusers', rooms[room], room);
          io.sockets.to(room).emit('updatechat', 'SERVER',  users[socket.username]['username'] + ' has disconnected', room, users[socket.username]['sessionid'], 'disconnect');
        }
        catch(err){

        }
      }
      for(var room in p2plist){
          io.sockets.to(room).emit('updateP2P', 'SERVER', '', room, users[socket.username]['sessionid'], 'OFFLINE');
          store.del(users[socket.username]['username'] + room)
      }
      store.del(users[socket.username]['username'])
      delete users[socket.username];

    }
    // echo globally that this client has left
  });
});