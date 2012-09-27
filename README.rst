*****
Development Server
*****

First make sure you have all the requirements installed to run a development server. Some servers such as Celery and node.js depend on Redis so they must be started in the right order.

Open Assembly Installation
####

We recommend PIP and VirtualEnv to satisfy dependencies.

	sudo apt-get install python-pip

	sudo pip install virtualenv

Now setup the structure of the development folder and create the OA virtualenv

	mkdir OA

	cd OA

	git clone git://github.com/fragro/Open-Assembly.git

	mkdir OA_ENV

	virtualenv OA_ENV

	source OA_ENV/bin/activate

	cd Open-Assembly/ver1_0

	pip install -r requirements.txt


The MongoDB server
####

This should be sufficient for debian servers.

    sudo apt-get install mongodb

Redis Server
####

Goto http://redis.io/download and download/install the newest stable version or follow these instructions.

If you aren't using Redis for anything else we recommend placing the redis-2.4.17 directory in the OA folder.

    
	wget http://redis.googlecode.com/files/redis-2.4.17.tar.gz

	tar xzf redis-2.4.17.tar.gz

	cd redis-2.4.17

	make

Node.js
####

Install node.js and npm on Ubuntu

	sudo apt-get install python-software-properties

	sudo add-apt-repository ppa:chris-lea/node.js

	sudo apt-get update

	sudo apt-get install nodejs npm

Or follow the instructions here: https://github.com/joyent/node/wiki/Installing-Node.js-via-package-manager


Solr
####

If you aren't using Solr for anything else we recommend placing the apache-solr-3.6.1 directory in the OA folder.

	wget http://apache.mesi.com.ar/lucene/solr/3.6.1/apache-solr-3.6.1.tgz

	tar xzf apache-solr-3.6.1.tgz

Now replace the schema.xml in your local version with OA's schema.xml, which contains the necessary hooks to our database. First remove the old schema. Assuming the Solr directory is in OA/

	rm apache-solr-3.6.1/example/solr/conf/schema.xml

Now grab the schema from Open-Assembly/solr/conf/schema.xml

	cp Open-Assembly/solr/conf/schema.xml apache-solr-3.6.1/example/solr/conf/

Now the Solr server should be ready to jive with our Django DB schema.


Run the Development Server
####

Now Open a Terminal, navigate to Open-Assembly/ver1_0/openassembly and Run the Django Server

	python manage.py syncdb

If syncdb fails the first time, a second try should succeed.

	python manage.py runserver

Start Redis Server
----

Open a new terminal, go to the location where you installed redis and run the following command.

	src/redis-server

WARNING: You must run the Redis server before running the node.js or Celery servers


Start Celery Server
----

	Navigate back to the Open-Assembly/ver1_0/openassembly folder where the Django server is located. OA uses django-celery to run background tasks. 

	python manage.py celeryd


For more debug information in Celery inlude the DEBUG flag.

	python manage.py celeryd -l DEBUG


Start Solr Server
----

Navigate to the OA/ directory in a new terminal.

	cd apache-solr-3.6.1/example

	java -jar start.jar

Usage
----

External hyperlinks, like 

You should be ready to go with your dev Redis, Django, Celery, Solr, and Node.js servers up and running. Using Chrome, Firefox, Safari, or Opera and goto `Admin Setup <http://localhost:8000/setup_admin/>`_ to create an administrative account with the username 'admin' and password 'password'. Now you can begin to create groups and test content to develop on.

For usage information checkout our `tutorial <http://www.youtube.com/watch?v=_TzoR66HcYM>`_


*****
Production Server
*****

To push to production we recommend Dotcloud. It is actually much easier to push OA to production through dotcloud when compared to setting up the development server, because the server stack is built automatically. With the following instructions you can deploy an online version of OA for free.


Using Dotcloud
####

Dotcloud makes deploying Open Assembly easy. First create an account with dotcloud and install the CLI

http://docs.dotcloud.com/0.4/firststeps/install/

Next you just need to create a sandbox app in dotcloud. Replace ''appname'' with what you want to call your deployment of OA.

	dotcloud create appname

Navigate to the Open-Assembly/ folder and push to dotcloud.

	dotcloud push appname

That's it! You deployed your own verstion of OA live. If you want to make your OA deployment scalable and reliable you will need to access the billing details from Dotcloud and your app to Live, but sandbox apps will work for small groups that don't mind using the dotcloud URL

Requires Setting of Email and Password within Settings and associated EMAIL_PASSWORD in Dotcloud environment variables

http://docs.dotcloud.com/guides/environment/

Another Host
####

Open Assembly is configured to use dotcloud but you
can use your own host fairly easily, you'll need to change the settings.py file in the project to
reflect your own Redis/MongoDB/Node/Celery Servers. If anyone has success deploying to a different host we would appreciate what requirements are involved.