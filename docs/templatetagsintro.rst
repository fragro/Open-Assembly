.. _templatetags:

***************************************
Decoupling Design and Development
***************************************

Open Assembly deviates from the traditional approach found in Django concerning `Views <https://docs.djangoproject.com/en/dev/topics/http/views/>`_. Instead of developing a views.py function for different types of content, we have a single view that loads template files, where template tags take the place of the logic traditionally found in views.py in a Django project.

So what does a template tag function look like?
##################################################

Template tags are similar to Django template tags if you are familiar with those. They can be easily added to html files. These templates are rendered before the page loads, so they can also be used to procedurally generate javascript code. Combining template tags and javascript can be quite powerful.

This function calls ``pp_consensus_get`` from the :mod:`consensustags` module and displays the interest attribute of the :class:`pirate_consensus.models.Consensus` object. There are a few things happening here within the ``pp_consensus_get`` function.

- Loads the parameter ``object`` into the local context of the Python/Djano function
- Performs the logic of the function
- Loads the results of the function into the ``pp_consensus`` context, which the HTML designer can access through the template

You can easily filter the data from the template tag's context using other templatetags found in Django libraries or elsewhere.

Example
--------------

.. code-block:: html

	<body>
		{% pp_consensus_get object=object.pk %}
			<div>
			    {% if pp_consensus.consensus.interest > 1000 %}

			    	<a href="{{object.get_absolute_url}}">{{ pp_consensus.consensus.interest|floatformat:0 }}</a>

			    {% else %}

			    	<a href="{{object.get_absolute_url}}">{{ pp_consensus.consensus.interest|floatformat:1 }}</a>

			    {% endif %}
			</div>
		{% endpp_consensus_get %}
	</body>


Context Variables
--------------------

As you can see the function relies on the ``object`` variable, which is loaded by the :mod:`oa_cache module`. For designers all you really need to know is that the following is available to you as Django template objects in any template you create. These are commonly used as parameters to template tag functions, or can be used to populate the template with contextual data you are presenting to the user.

:object: :class:`django.db.models.Model` object
:user: :class:`django.contrib.auth.User` object of logged in user
:start: start integer for pagination
:end: end integer for pagination
:dimension: dimension string for sorting or filtering, usually reserved for lists

Here's an example of how one might use these objects in a template.

.. code-block:: html

	<h2><a href="{{object.get_absolute_url}}">{{object.summary}}</a></h2>

	{% if user == object %}

		Welcome home {{user.username}}.

		{% pp_get_messages start=start end=end user=user %}

			{% for message in pp_messages.all reversed %}

				<div> 

					{{note.description}}

				</div>

			{% endfor %}

		{% endpp_get_messages %}

	{% endif %}



pp_url Links
#################

Django allows you to drop links into your templates fairly easily. You need to use the :ref:`pirate_core.templatetags.pp_url` template tag.

This block tag will produce a url that will link to the designated view or pattern
name, and then will optionally populate the request passed to that view with
either a specific ORM object, or a numerical range (start...end), as long as
the pirate_core.url_middleware.UrlMiddleware is included in the projects'
MIDDLEWARE_CLASSES. Any kwargs included in addition to "view", "object", "start"
and "end" will be passed to redirect in order to produce the url for the designated
view.

The default value for "view" is "pp-page", which expects that the kwarg "template" be
included, passing in the name of the template being linked to.

For example:

.. code-block:: html

	{% pp_url object=object template="filename.html" %}

	{% pp_url template="filename.html" start=0 end=30 dimension="n" %}

	{% pp_url template="filename.html" %}


Try the following from the Django shell from ``manage.py`` in the openassembly directory.

.. code-block:: bash

	python manage.py shell

.. code-block:: bash

	>>> from django import template
	>>> from pirate_topics.models import Topic
	>>> topic = Topic(summary="A test topic.", shortname="test-topic", description="test", group_members=0)
	>>> topic.save()
	>>> load = "{% load pp_url %}"

	>>> ts = "{% pp_url template='example.html' object=topic %}"
	>>> template.Template(load + ts).render(template.Context({'topic':topic}))
	u'/p/example/k-test-topic'

	>>> ts = "{% pp_url template='example.html' object=topic start=0 end=30 %}"
	>>> template.Template(load + ts).render(template.Context({'topic':topic}))
	u'/p/example/k-test-topic/s-0/e-30'

	>>> ts = "{% pp_url template='example.html' start=0 end=30 dimension='new' %}"
	>>> template.Template(load + ts).render(template.Context({'topic':topic}))
	u'/p/example/s-0/e-30/d-new'

	>>> topic.delete()