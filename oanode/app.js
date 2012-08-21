//redis specific
var port = 6379;

var app = require('express').createServer(),
    redis = require('socket.io/node_modules/redis'),
    io = require('socket.io').listen(app);

var pub = redis.createClient(port, "localhost");
var sub = redis.createClient(port, "localhost");
var store = redis.createClient(port, "localhost");
pub.auth('pass', function(){console.log("adentro! pub")});
sub.auth('pass', function(){console.log("adentro! sub")});
store.auth('pass', function(){console.log("adentro! store")});

io.configure( function(){
	io.enable('browser client minification');  // send minified client
	io.enable('browser client etag');          // apply etag caching logic based on version number
	io.enable('browser client gzip');          // gzip the file
	io.set('log level', 1);                    // reduce logging
	io.set('transports', [                     // enable all transports (optional if you want flashsocket)
	    'websocket'
	  , 'flashsocket'
	  , 'htmlfile'
	  , 'xhr-polling'
	  , 'jsonp-polling'
	]);
	var RedisStore = require('socket.io/lib/stores/redis');
	io.set('store', new RedisStore({redisPub:pub, redisSub:sub, redisClient:store}));
});
console.log('io configured');

app.listen(8080);

var buffer = [];
io.sockets.on('connection', function(client){
	var Room = "";
    client.on("setNickAndRoom", function(nick, fn){
    	fn({msg : "Hello " + nick.nick});
    	client.join(nick.room);
    	Room = nick.room;
    	client.broadcast.to(Room).json.send({ msg: "Se conecto al room: " + nick.room, nick : nick });
    });

    client.on('message', function(message, fn){
        var msg = message; //{ message: [client.sessionId, message] };
        buffer.push(msg);
        if (buffer.length > 15)
        	buffer.shift();
        client.broadcast.to(Room).json.send(msg);
        fn(msg);
    });

    client.on('disconnect', function(){
    	client.broadcast.to(Room).json.send({ msg: "Se desconecto"});
    });
    
});