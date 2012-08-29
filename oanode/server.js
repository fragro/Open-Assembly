
var fs = require('fs');
var app = require('express').createServer(),
    redis = require('socket.io/node_modules/redis'),
    io = require('socket.io').listen(app);

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

 }
catch(e){
  //running on dev server
  var nodeport = 8080;
  var port = 6379;
  var host = 'localhost';
  var sub = redis.createClient(port, host);
  var store = redis.createClient(port, host); 
}
// 


//var store = redis.createClient(port, host);
// pub.auth('pass', function(){console.log("adentro! pub")});
// sub.auth('pass', function(){console.log("adentro! sub")});
// store.auth('pass', function(){console.log("adentro! store")});

app.listen(nodeport);

//returns new_user, true if this user has joined this chat for the first time this session
function init_user(users, username, sessionid, socketid, room){
  if(room != null){
    var u1 = users[sessionid];
    var new_user = true;
    if(u1){
      console.log(u1);
      if(u1['chats'][room] == 1){
        new_user = false;
      }
      else{
        u1['chats'][room] = 1;
      }
    }
    else{
      var chatlist = {};
      chatlist[room] = 1; 
      users[sessionid] = {'username': username, 'socketid': socketid, 'sessionid': sessionid, 'chats': chatlist};
    }
    return new_user;
  }
  else{
    users[sessionid] = {'username': username, 'socketid': socketid, 'sessionid': sessionid, 'chats': {}};
  }
}

function init_room(rooms, room, username){

  var r1 = rooms[room];
  if(r1){
    rooms[room][username] = 1;
  }
  else{
    rooms[room] = {};
    rooms[room][username] = 1;
  }
}

//CHAT SOCKETIO CODE
// usernames which are currently connected
var users = {};
var rooms = {};


//when redis sends us a message about a channel we are subscribed to: logic
sub.on("message", function (channel, message) {
    console.log("client1 channel " + channel + ": " + message);
    try{
      store.get(channel, function (err, reply) {
        if(reply != null){
          console.log('reply from redis: ' + reply.toString());
          var sessionid = reply.toString();
          console.log(users[sessionid]['socketid']);
          io.sockets.socket(users[sessionid]['socketid']).emit('updateUI', message); 
        }
        else{
          console.log(store.keys('*'));
        }
      });

    }
    catch(err){

    }
});

io.sockets.on('connection', function (socket) {

  // when the client emits 'sendchat', this listens and executes
  socket.on('sendchat', function (data, room) {
    // we tell the client to execute 'updatechat' with 2 parameters
      try{
        io.sockets.to(room).emit('updatechat', users[socket.username]['username'], data, room, users[socket.username]['sessionid']);
      }
      catch(err){
        io.sockets.socket(socket.id).emit('updatechat', 'SERVER', 'Still connecting. Wait a few seconds please.', room);
      }
  });

  //when the user subscribes to dynamic events through socket.io, register the redis SUB
  socket.on('subscribe', function(username, sessionid){
    console.log('subscribed to ' + username);
    //initialize user so we can responsd to the right socket for real-time events
    init_user(users, username, sessionid, socket.id, null);
    sub.subscribe(username);
    store.set(username, sessionid);
    //store.expire(username, -1)
  });

  // when the client emits 'adduser', this listens and executes
  socket.on('adduser', function(username, sessionid, room){
    socket.set('room', room, function() { console.log('room ' + room + ' saved'); } );
    socket.join(room);
    // we store the username in the socket session for this client
    socket.username = sessionid;
    // add the client's username to the global list
    new_user = init_user(users, username, sessionid, socket.id, room);
    init_room(rooms, room, username);
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

      // update list of users in chat, client-side
      for(var room in chatlist){
        //first check to 
        delete rooms[room][users[socket.username]['username']]
        io.sockets.to(room).emit('updateusers', rooms[room], room);
        io.sockets.to(room).emit('updatechat', 'SERVER',  users[socket.username]['username'] + ' has disconnected', room, users[socket.username]['sessionid'], 'disconnect');

      }
      store.del(users[socket.username]['username'])
      delete users[socket.username];

    }
    // echo globally that this client has left
  });
});