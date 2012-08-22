
var fs = require('fs');
var app = require('express').createServer(),
    redis = require('socket.io/node_modules/redis'),
    io = require('socket.io').listen(app);

process.on('SIGTERM', function () {
  console.log('Got SIGTERM, exiting...');
  process.exit(0);
});

//dotcloud environment parametes for hooking into our own redis server
//try{
var env = JSON.parse(fs.readFileSync('/home/dotcloud/environment.json', 'utf-8'));
port = env['DOTCLOUD_CACHE_REDIS_PORT'];
host = env['DOTCLOUD_CACHE_REDIS_HOST'];

// /*}
// catch(e){
//   var port = 6379;
//   var host = 'localhost';
// }
// */
// var pub = redis.createClient(port, host);
// var sub = redis.createClient(port, host);
// var store = redis.createClient(port, host);
// pub.auth('pass', function(){console.log("adentro! pub")});
// sub.auth('pass', function(){console.log("adentro! sub")});
// store.auth('pass', function(){console.log("adentro! store")});

app.listen(8080);

function init_user(users, username, sessionid, socketid, room){
  var u1 = users[sessionid];
  if(u1){
    console.log(u1);
    u1['chats'][room] = 1;
  }
  else{
    var chatlist = {};
    chatlist[room] = 1; 
    users[sessionid] = {'username': username, 'socketid': socketid, 'sessionid': sessionid, 'chats': chatlist};
  }
}

//CHAT SOCKETIO CODE
// usernames which are currently connected to the chat
var users = {};
//list of users for each chat room to direct messages

io.sockets.on('connection', function (socket) {

  // when the client emits 'sendchat', this listens and executes
  socket.on('sendchat', function (data, room) {
    // we tell the client to execute 'updatechat' with 2 parameters
      io.sockets.to(room).emit('updatechat', users[socket.username]['username'], data, room);
  });

  // when the client emits 'adduser', this listens and executes
  socket.on('adduser', function(username, sessionid, room){
    socket.set('room', room, function() { console.log('room ' + room + ' saved'); } );
    socket.join(room);
    // we store the username in the socket session for this client
    socket.username = sessionid;
    // add the client's username to the global list
    init_user(users, username, sessionid, socket.id, room);
    //init_chat(rooms, socket.id, room);
    // echo to client they've connected
    socket.to(room).emit('updatechat', 'SERVER', 'you have connected', room);
    // echo globally (all clients) that a person has connected
    socket.broadcast.to(room).emit('updatechat', 'SERVER', username + ' has connected', room);
    // update the list of users in chat, client-side
    io.sockets.to(room).emit('updateusers', users, room);
  });

  // when the user disconnects.. perform this
  socket.on('disconnect', function(){
    // remove the username from global usernames list
    user = users[socket.username]
    if(user){
      chatlist = user['chats']
      //delete users[socket.username];
      // update list of users in chat, client-side
      for(var room in chatlist){
        io.sockets.to(room).emit('updateusers', users, room);
      }
    }
    // echo globally that this client has left
    socket.broadcast.to(room).emit('updatechat', 'SERVER', users[socket.username]['username'] + ' has disconnected', room);
  });
});