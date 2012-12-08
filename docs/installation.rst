*************************
Installing Development Server
*************************

First make sure you have all the requirements installed to run a development server. Some servers such as Celery and node.js depend on Redis so they must be started in the right order.

Open Assembly Installation
############################

Install `Git <http://git-scm.com/>`_ and HG if these version control libraries isn't already installed.

.. code-block:: bash

	sudo apt-get install git-core mercurial

We recommend PIP and VirtualEnv to satisfy dependencies.

.. code-block:: bash

	sudo apt-get install python-pip

	sudo pip install virtualenv

Now setup the structure of the development folder and create the OA virtualenv

.. code-block:: bash

	mkdir OA

	cd OA

	git clone git://github.com/fragro/Open-Assembly.git

	mkdir OA_ENV

	virtualenv OA_ENV

	source OA_ENV/bin/activate

	cd Open-Assembly/ver1_0

	pip install -r requirements.txt


The MongoDB server
############################

This should be sufficient for debian servers.

.. code-block:: bash

    sudo apt-get install mongodb

Redis Server
############################

Go `here <http://redis.io/download and download/install>`_ and install the newest stable version or follow these instructions.

If you aren't using Redis for anything else we recommend placing the redis-2.4.17 directory in the OA folder.

.. code-block:: bash
    
	wget http://redis.googlecode.com/files/redis-2.4.17.tar.gz

	tar xzf redis-2.4.17.tar.gz

	cd redis-2.4.17

	make

Node.js
############################

Install from source (check `here <http://nodejs.org/download/>`_ for the latest version):

.. code-block:: bash

	wget http://nodejs.org/dist/v0.8.11/node-v0.8.11.tar.gz

	tar xzf node-v0.8.11.tar.gz

	cd node-v0.8.11

	make

	sudo make install


Now you need to install the dependencies. Goto Open-Assembly/oanode/ and run the command

.. code-block:: bash

	npm install

Solr
############################

If you aren't using Solr for anything else we recommend placing the apache-solr-3.6.1 directory in the OA folder.

.. code-block:: bash

	wget http://apache.mesi.com.ar/lucene/solr/3.6.1/apache-solr-3.6.1.tgz

	tar xzf apache-solr-3.6.1.tgz

Now replace the schema.xml in your local version with OA's schema.xml, which contains the necessary hooks to our database. First remove the old schema. Assuming the Solr directory is in OA/

.. code-block:: bash

	rm apache-solr-3.6.1/example/solr/conf/schema.xml

Now grab the schema from Open-Assembly/solr/conf/schema.xml

.. code-block:: bash

	cp Open-Assembly/solr/conf/schema.xml apache-solr-3.6.1/example/solr/conf/

Now the Solr server should be ready to jive with our Django DB schema.


Run the Development Server
############################

Now Open a Terminal, navigate to Open-Assembly/ver1_0/openassembly and Run the Django Server. Remember that if you installed your dependencies in a virtualenv using the command ``source OA_ENV/bin/activate`` you must be in that virtual environment when running these from your shell.

.. code-block:: bash

	python manage.py syncdb


Next we will transfer the static files from the various modules into our static_dev_server folder. You need to run this command every time you add a new file to a static folder or add a new module with static files. `More on static files in Django <https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/>`_.

.. code-block:: bash

    python manage.py collectstatic

We want to rebuild the index in Solr once you have accumulated some data in your development environment, if you want to modify the search design or code. If this is your first time starting the server you can skip this step. The production server will take care of this with a cron job.

.. code-block:: bash

    python manage.py rebuild_index

If syncdb fails the first time, a second try should succeed.

.. code-block:: bash

	python manage.py runserver


Start Redis Server
----------------------------

Open a new terminal, go to the location where you installed redis and run the following command.

.. code-block:: bash

	src/redis-server

WARNING: You must run the Redis server before running the node.js or Celery servers


Start Celery Server
----------------------------

Navigate back to the Open-Assembly/ver1_0/openassembly folder where the Django server is located. OA uses django-celery to run background tasks. 

.. code-block:: bash

	python manage.py celeryd


For more debug information in Celery inlude the DEBUG flag.

.. code-block:: bash

	python manage.py celeryd -l DEBUG


Start Solr Server
----------------------------

Navigate to the OA/ directory in a new terminal.

.. code-block:: bash

	cd apache-solr-3.6.1/example

	java -jar start.jar


Start Node.js Server
----------------------------

Navigate to the Open-Assembly/oanode directory in a new terminal.

.. code-block:: bash

	node server.js

Amazon S3 Support
---------------------------

To setup your OA application for images, create a file called 'local_environment.json' in your home folder. The contents should look something like this, except substituted for your own variables from S3. The mountpoint "/home/user/media/" could be any existing directory on your filesystem. S3FS_ACCESSKEY, S3FS_SECRETKEY and S3FS_BUCKET must be setup from your `S3 management console <http://aws.amazon.com/console/>`_. If this is not available the django-storages will default to HashStorage.

.. code-block:: bash

	{"S3FS_ACCESSKEY": "ASIODUAS27FSAS2",
		"S3FS_BUCKET": "openassembly-store",
		"S3FS_MOUNTPOINT": "/home/user/media/",
		"S3FS_SECRETKEY": "aos8ddas8foafkl2l2oka9sk9akdo2"
	}

Usage
----------------------------

You should be ready to go with your dev Redis, Django, Celery, Solr, and Node.js servers up and running. Using Chrome, Firefox, Safari, or Opera and goto `Admin Setup <http://localhost:8000/setup_admin/>`_ to create an administrative account with the username 'admin' and password 'password'. Now you can begin to create groups and test content to develop on.

For help in understanind the OA user interface checkout our `tutorial <http://www.youtube.com/watch?v=_TzoR66HcYM>`_.


***********************************
Deploying Production Server
***********************************

To push to production we recommend Dotcloud. It is actually much easier to push OA to production through dotcloud when compared to setting up the development server, because the server stack is built automatically. With the following instructions you can deploy an online version of OA for free.


Using Dotcloud
############################

Dotcloud makes deploying Open Assembly easy. First create an account with dotcloud and install the CLI `here <http://docs.dotcloud.com/0.9/firststeps/install/>`_

First clone from git if you did not do so setting up a development server. This leads to the development repository, which may be unstable from time to time. We are starting a release cycle and will soon have a stable package available.

.. code-block:: bash

	git clone git://github.com/fragro/Open-Assembly.git

Next you just need to create a sandbox app in dotcloud. Replace ''appname'' with what you want to call your deployment of OA.

.. code-block:: bash

	dotcloud create appname

First you need to specify some important environment variables from S3 and your Email host. First the required environment variables for S3 Amazon cloud server, where image files are stored.

Amazon S3 Support
---------------------------

To setup your OA application for images, create a file called 'local_environment.json' in your home folder. The contents should look something like this, except substituted for your own variables from S3. The mountpoint "/home/user/media/" could be any existing directory on your filesystem. S3FS_ACCESSKEY, S3FS_SECRETKEY and S3FS_BUCKET must be setup from your `S3 management console <http://aws.amazon.com/console/>`_.

.. code-block:: bash

	dotcloud env set \
	    'S3FS_ACCESSKEY=MYSECRETACCESSKEY' \
	    'S3FS_BUCKET=openassembly-store' \
	    'S3FS_SECRETKEY=MYSECRETS3FSKEY'

Note if you do not have S3 or want to use a different method of file/image storage, please see the settings.py file in ver1_0/openassembly and change the value of DEFAULT_FILE_STORAGE to specify the storages backed you want. For more information on the different backends, see `django storages <http://django-storages.readthedocs.org/en/latest/>`_ documentation .

OA also requires Setting of EMAIL_HOST_USER, EMAIL_HOST and EMAIL_PASSWORD within the dotcloud environment variables. This allows you to easily include your own email host.

You can modify the local version before you push to dotcloud.

.. code-block:: bash

	dotcloud env set \
		'EMAIL_PASSWORD=mysecretpassword' \
		'EMAIL_HOST_USER=myemail@gmail.com' \
		'EMAIL_HOST=smtp.gmail.com' \

.. code-block:: python

    DEFAULT_FROM_EMAIL = env['EMAIL_HOST_USER']
    EMAIL_USE_TLS = True
    EMAIL_HOST = env['EMAIL_HOST']
    EMAIL_HOST_USER = env['EMAIL_HOST_USER']
    EMAIL_HOST_PASSWORD = env['EMAIL_PASSWORD']
    EMAIL_PORT = 587

You also must set the EMAIL_PASSWORD environment variable in `Dotcloud environment variables <http://docs.dotcloud.com/guides/environment/>`_.

.. code-block:: bash

	dotcloud var set appname EMAIL_PASSWORD=mysecretpassword

You'll also need to setup reCaptcha to keep those pesky spam bots off your back. Go to the `reCaptcha <http://www.google.com/recaptcha/whyrecaptcha>`_  website to get a Public and Private key from Google. Set those environment
variables the same as you would the S3 settings.

.. code-block:: bash

	dotcloud env set \
	    'S3FS_ACCESSKEY=MYSECRETACCESSKEY' \
	    'S3FS_BUCKET=openassembly-store' \
	    'S3FS_SECRETKEY=MYSECRETS3FSKEY'


Then navigate to the Open-Assembly/ folder and connect/push to dotcloud.

.. code-block:: bash

	dotcloud connect appname
	dotcloud push

That's it! You deployed your own verstion of OA live and at the end of output there should be a url. If the push fails for some reason try again. If the push times out, go to dashboard.dotcloud.com and check on the status of your OA install live. If you want to make your OA deployment scalable and reliable you will need to access the billing details from Dotcloud and your app to Live, but sandbox apps will work for small groups that don't mind using the dotcloud URL.


Other Hosts
############################

Open Assembly is configured to use dotcloud but you can use your own host fairly easily with the pip requirements file, you'll need to change the settings.py file in the project to reflect your own Redis/MongoDB/Node/Celery Servers. If anyone has success deploying to a different host we would appreciate feedback on your experience.