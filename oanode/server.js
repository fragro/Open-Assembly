
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

 }
catch(e){
  //running on dev server
  var nodeport = 8080;
  var port = 6379;
  var host = 'localhost';
}
// 
console.log(env['DOTCLOUD_CACHE_REDIS_PORT']);
console.log(env['DOTCLOUD_CACHE_REDIS_HOST']);

var pub = redis.createClient(port, host);
console.log('output');
pub.auth(env['DOTCLOUD_CACHE_REDIS_PASSSWORD'])

rc.on('ready', function(){
  console.log('this doesn\'t get printed');
  // move this out of ready handler
  // rc.auth('password');
});

// can't hurt to attach an error handler as well, if you want to
rc.on('error', function (e) {
  console.log(e);
});


//var sub = redis.createClient(port, host);
//var store = redis.createClient(port, host);
// pub.auth('pass', function(){console.log("adentro! pub")});
// sub.auth('pass', function(){console.log("adentro! sub")});
// store.auth('pass', function(){console.log("adentro! store")});

app.listen(nodeport);

//returns new_user, true if this user has joined this chat for the first time this session
function init_user(users, username, sessionid, socketid, room){
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

function init_room(rooms, room, username){

  var r1 = rooms[room];
  if(r1){
    rooms[room][username] = 1;
  }
  else{
    rooms[room] = {};
    rooms[room][username] = 1;
  }
  return new_room;
}

//CHAT SOCKETIO CODE
// usernames which are currently connected to the chat
var users = {};
var rooms = {};
//list of users for each chat room to direct messages

io.sockets.on('connection', function (socket) {

  // when the client emits 'sendchat', this listens and executes
  socket.on('sendchat', function (data, room) {
    // we tell the client to execute 'updatechat' with 2 parameters
      io.sockets.to(room).emit('updatechat', users[socket.username]['username'], data, room, users[socket.username]['sessionid']);

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
      //init_chat(rooms, socket.id, room);
      // echo to client they've connected
      // echo globally (all clients) that a person has connected
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
      delete users[socket.username];

    }
    // echo globally that this client has left
  });
});