
from django.http import HttpResponseRedirect
from django.contrib.contenttypes.models import ContentType

from customtags.decorators import block
from pirate_core import FormMixin, ComboFormFactory, namespace_get
from django import template

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

# this function assignment lets us reuse the same code block a bunch of places
get_namespace = namespace_get('pp_core')

@block
def pp_combo_form(context, nodelist, *args, **kwargs):
    """

    This tag is used to merge two separate forms into one form.  It does this
    by performing three actions:

    (1) It merges the fields of two separate forms into a single form with
        unified error messaging, and uniqueness among field names.
    (2) When provided a POST argument that matches its internally-determined
        form id, it will process that form in order to produce any error messages
    (3) When provided with a POST argument, it will assume that all forms
        passed in as arguments will also have been instantiated with that same POST.
        The validity of the MultiForm it produces will be tested; the MultiForm
        iteself will loop over the individual sub-forms testing to see if each is 
        valid as well.  Any errors discovered will be added to its own errors.
    (4) If the MultiForm is valid (and by implication the sub-forms are valid as well),
        then the pp_multi_form tag will call save() on the MultiForm with commit=True, 
        which in turn will call save() on each of the sub-forms. If a path is not, 
        provided, however, the tag will call save() on the MultiForm with commit=False.
    (5) If a path argument is specified and the MultiForm is successfully saved, 
        then the tag will raise the HttpRedirectException indicating a redirect 
        to the specified path.  Otherwise, it will just add the MultiForm to the context.

    The pp_multi_form tag is compatible with form tags with the following
    characteristics:

    - Just like other form tags, these form tags should instantiate their form with
      the POST if it is provided, and instantiate their form without any POST if it 
      is not provided.
    - These form tags should only raise the HttpRedirectException when a
      path is provided as an argument. If no path is provided but a POST is, then
      the form should be instantiated and saved (if valid), and then added
      to the context.  If no POST is provided, then the form should just be
      instantiated and added to the context.
    - The forms produced by these tags must contain a save() method that takes
      the "commit" kwarg to determine whether a save() should hit the database.
      This save method should be called with commit=True when a valid POST and 
      a path are both supplied, but it should be called with commit=False if
      a valid path  is supplied but a valid POST is not.

    Setup...

        >>> from django import template
        >>> from pirate_core import ComboFormFactory, HttpRedirectException
        >>> from pirate_issues.models import Issue, Topic
        >>> from pirate_issues.templatetags.issuetags import IssueForm
        >>> from pirate_extensions.templatetags.taggingtags import TagForm
        >>> from tagging.models import Tag, TaggedItem

        >>> template.add_to_builtins('customtags.templatetags.customtags')

        >>> topic = Topic(text="Opinions and Views.")
        >>> topic.save()
        >>> issue = Issue(text="My opinion on tax cuts.", topic=topic)
        >>> issue.save()
        >>> Tag.objects.update_tags(issue, "taxes congress")

        >>> ts = '''
        ...      {% pp_issue_form POST=post issue=issue %}
        ...        {% pp_tag_form object=pp_issue.form.instance POST=post %}
        ...          {% pp_combo_form pp_issue.form pp_tags.form POST=post path="/" %}
        ...            {{ pp_core.combo_form.as_p }}
        ...          {% endpp_combo_form %}
        ...        {% endpp_tag_form %}
        ...      {% endpp_issue_form %}
        ...      '''

        >>> result1 = template.Template(ts).render(template.Context({"post":None, "issue":None}))
        >>> " ".join(result1.split())
        u'<p><label for="id_topic">Topic:</label> <select name="topic" id="id_topic"> <option value="" selected="selected">---------</option> <option value="1">Opinions and Views.</option> </select></p> <p><label for="id_name">Name:</label> <input id="id_name" type="text" name="name" value="DEF" maxlength="140" /></p> <p><label for="id_text">Text:</label> <textarea id="id_text" rows="10" cols="40" name="text"></textarea></p> <p><label for="id_interest">Interest:</label> <input type="text" name="interest" value="0.0" id="id_interest" /></p> <p><label for="id_controversy">Controversy:</label> <input type="text" name="controversy" value="0.0" id="id_controversy" /></p> <p><label for="id_comments">Comments:</label> <input type="text" name="comments" value="0" id="id_comments" /></p> <p><label for="id_tags">Tags:</label> <input type="text" name="tags" id="id_tags" /></p> <p><label for="id_form_id_0">Form id:</label> <input type="hidden" name="form_id_0" value="Fc8b6368985a9ad50492ccd96ee7de9e3" id="id_form_id_0" /><input type="hidden" name="form_id_1" value="Ff5fe7ac70fa4aab31f26632adfc4e4fe" id="id_form_id_1" /><input type="hidden" name="form_id_2" value="F02c06e8500480e06cecc20e409912a77" id="id_form_id_2" /></p>'


    If an issue is included in the results, then that issue's tags should appear in the form.

        >>> result3 = template.Template(ts).render(template.Context({"post":None, "issue":issue}))
        >>> " ".join(result3.split())
        u'<p><label for="id_topic">Topic:</label> <select name="topic" id="id_topic"> <option value="">---------</option> <option value="1" selected="selected">Opinions and Views.</option> </select></p> <p><label for="id_name">Name:</label> <input id="id_name" type="text" name="name" value="DEF" maxlength="140" /></p> <p><label for="id_text">Text:</label> <textarea id="id_text" rows="10" cols="40" name="text">My opinion on tax cuts.</textarea></p> <p><label for="id_interest">Interest:</label> <input type="text" name="interest" value="0.0" id="id_interest" /></p> <p><label for="id_controversy">Controversy:</label> <input type="text" name="controversy" value="0.0" id="id_controversy" /></p> <p><label for="id_comments">Comments:</label> <input type="text" name="comments" value="0" id="id_comments" /></p> <p><label for="id_tags">Tags:</label> <input type="text" name="tags" id="id_tags" /></p> <p><label for="id_form_id_0">Form id:</label> <input type="hidden" name="form_id_0" value="F3f08dc1112a3c32ed9628840b9f40dbe" id="id_form_id_0" /><input type="hidden" name="form_id_1" value="Fe8ac33ce836a7f9e497dd37c29281eaa" id="id_form_id_1" /><input type="hidden" name="form_id_2" value="F55b12f88c3c1bbc1272b5f1720883e25" id="id_form_id_2" /></p>'

    Now, this tests whether or not a form submission including a POST dictionary works.

        >>> POST = {}
        >>> POST["name"] = "Increase the pay of members of congress."
        >>> POST["text"] = issue.text
        >>> POST["topic"] = issue.topic.pk
        >>> POST["form_id_0"] = IssueForm.form_id(instance=issue)
        >>> POST["tags"] = "congress budget"
        >>> POST["form_id_1"] = TagForm.form_id(instance=issue)

    As part of the setup, figure out what the ComboForm's form_id field name is going to be

        >>> form1 = IssueForm.create(instance=issue) # ComboForm needs form1 to be valid.
        >>> form2 = TagForm.create(instance=form1.instance) # form2 needs to be valid.
        >>> ComboForm = ComboFormFactory(form1, form2).get_form_class()
        >>> POST["form_id_2"] = ComboForm.form_id()

        >>> try:
        ...   template.Template(ts).render(template.Context({"post":POST, "issue":issue}))
        ... except HttpRedirectException, e:
        ...   exc = e.http_response_redirect
        ... except template.TemplateSyntaxError, e:
        ...   if hasattr(e, 'exc_info') and e.exc_info[0] is HttpRedirectException:
        ...     exc = e.exc_info[1].http_response_redirect
        >>> exc
        <django.http.HttpResponseRedirect object at ...>

        >>> issues = Issue.objects.filter(name="Increase the pay of members of congress.")
        >>> len(list(issues))
        1
        >>> tags = Tag.objects.get_for_object(issues[0])
        >>> tags
        [<Tag: budget>, <Tag: congress>]
        >>> items = TaggedItem.objects.get_by_model(Issue, tags)
        >>> items
        [<Issue: Increase the pay of members of congress.>]

        >>> Issue.objects.all().delete()
        >>> TaggedItem.objects.all().delete()
        >>> Tag.objects.all().delete()
        >>> Topic.objects.all().delete()
    """

    context.push()
    namespace = get_namespace(context)

    POST    = kwargs.get("POST", None)
    path    = kwargs.get('path', None) 
    as_name = kwargs.get('as_name', None)
   
    form = ComboFormFactory(*args).create_form(POST, path)

    if as_name is not None:
        context[asname] = form
    else:
        namespace['combo_form'] = form

    output = nodelist.render(context)
    context.pop()

    return output
