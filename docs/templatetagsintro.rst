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

Django allows you to drop links into your templates fairly easily.