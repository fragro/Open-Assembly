from django import template
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from pirate_core import HttpRedirectException, namespace_get, FormMixin
from pirate_issues.models import Problem
from pirate_topics.models import Topic
from pirate_consensus.models import UpDownVote, Consensus
from django.utils.translation import ugettext as _
from pirate_reputation.models import ReputationDimension
from pirate_core.helpers import clean_html

from pirate_signals.models import aso_rep_event, relationship_event

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

'''
This file contains all of the tags that pertain to Issue objects, in order to fetch one
issue, a list of issues, or to add or update an issue.
'''


# this function assignment lets us reuse the same code block a bunch of places
get_namespace = namespace_get('pp_issue')


@block
def pp_get_issue(context, nodelist, *args, **kwargs):
    '''
    This block tag will grab an issue based on an object pair (str, obj_id) passed in
    as an argument (assigned to object), and will then put that issue into the context.

    The (str, obj_id) pair will be available via request.object.  In order to populate 
    request.objcect, the page in question should be accessed by via a url created as follows:

    {% url pp-page object="issue" id=issue.id template="filename.html" %}
    '''

    context.push()
    namespace = get_namespace(context)

    # this tag only works if a valid pair is assigned to the 'object=' argument
    object = kwargs.pop('object', None)
    if object is None:
        raise ValueError("pp-get-issue tag requires that a (str, obj_id) pair be passed "
                             "to it assigned to the 'object=' argument, and that the str "
                             "be assigned the string value 'issue'.")
    
    namespace['issue'] = object
    
    #grab consensus objects and votes related to this issue
    #namespace['consensus'] = get_object_or_404(Consensus,object_pk=object.id)
    #namespace['upvotes'] = len(UpDownVote.objects.filter(parent=namespace['consensus'],vote_type=1))
    #namespace['downvotes'] = len(UpDownVote.objects.filter(parent=namespace['consensus'],vote_type=-1))
    #namespace['neutralvotes'] = len(UpDownVote.objects.filter(parent=namespace['consensus'],vote_type=0))
    
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_get_issue_list(context, nodelist, *args, **kwargs):
 

    """
    return output will optionally look for a topic or a 
    rng of items in order to further refine the list.
    
    *Possible Dimension Arguments:
        ** hot: highly intereresting articles based on issue.interest
        ** new: latest content based on submit date
        ** top: those with the most votes
        ** cont: controversial issues that have the userbased divided
        ** numc: Ranked by number of commefrom pirate_issues.models import Topic, Issue, Rankingnts
    
    The default dimension is "new" when no dimension is specified.

    In order to generate a url that will provide rng information to this tag via
    request.rng, use a url tag of the following form:
    
    {% url pp-page template="filename.html" start=0 end=20 %}

    In this way, the tag can be invoked as follows:

    {% pp-issue-list topic=topic rng=request.rng dimension="dim" %}
       Do stuff with {{ pp-issue.issue_list }}
    {% endpp-issue-list %}
    
    >>> from django import template
    >>> from django import forms
    >>> from django.shortcuts import get_object_or_404
    >>> from django.http import HttpResponseRedirect
    >>> import datetime
    >>> from django.contrib.contenttypes.models import ContentType
    >>> from native_tags.decorators import block
    >>> from pirate_core import HttpRedirectException, namespace_get, FormMixin
    >>> from pirate_issues.models import Topic, Issue, Ranking
    >>> from pirate_consensus.models import UpDownVote, Consensus
    >>> from django.utils.translation import ugettext as _
    
    >>> topic1 = Topic(text = "taxes")
    >>> topic2 = Topic(text = "debt")
    >>> topic1.save()
    >>> topic2.save()
    >>> issue1 = Issue(name="nom1", text="argue",topic=topic1)
    >>> issue2 = Issue(name="nom2", text="rabblerabble",topic=topic2)
    >>> issue3 = Issue(name="nom3", text="grr",topic=topic1)
    >>> issue1.save()
    >>> issue2.save()
    >>> issue3.save()
    >>> issue_list = Issue.objects.all()
    
    >>> for i in issue_list: contype=ContentType.objects.get_for_model(Issue); obj_pk=i.pk; cons, is_new = Consensus.objects.get_or_create(content_type=contype,object_pk=obj_pk)
    
    >>> issue_list.filter(topic__id=topic1.id)
    [<Issue: nom1>, <Issue: nom3>]

    >>> consensus_list = Consensus.objects.all()
    >>> consensus_list
    [<Consensus: issue: 3>, <Consensus: issue: 4>, <Consensus: issue: 5>]
    
    #>>> consensus_list.filter(content_type__name=u'issue')
    #[<Consensus: issue: 3>, <Consensus: issue: 4>, <Consensus: issue: 5>]
    
    >>> issue_list = Issue.objects.all()
    >>> issue_list.order_by('-submit_date')
    [<Issue: nom3>, <Issue: nom2>, <Issue: nom1>]
    
    #Later we can add some voting code to make these tests more interesting
    
    >>> issue_list.order_by('-interest')
    [<Issue: nom1>, <Issue: nom2>, <Issue: nom3>]
    >>> issue_list.order_by('-controversy')
    [<Issue: nom1>, <Issue: nom2>, <Issue: nom3>]
    >>> issue_list.order_by('-comments')
    [<Issue: nom1>, <Issue: nom2>, <Issue: nom3>]
    
    >>> topic = Topic(text="A test topic.")
    >>> topic.save()

    >>> ts = '{% pp_url template="issuelist_test.html" object=topic %}'
    >>> url = template.Template(ts).render(template.Context({'topic':topic}))

    >>> from django.test.client import Client
    >>> c = Client()
    >>> response = c.get(url)
    >>> response.content
    "\\n\\n    \\n        grr\\n\\n    \\n        rabblerabble\\n\\n    \\n        argue\\n\\n    \\n\\n\\n"
    
    #These don't work
    ###>>> issue1.delete(); issue2.delete(); issue3.delete(); 
    ###>>> topic1.delete(); topic2.delete()
    """
    context.push()
    namespace = get_namespace(context)

    #user  = kwargs.pop('user',  None)
    topic = kwargs.pop('topic', None)
    start   = kwargs.pop('start', None)
    end   = kwargs.pop('end', None)
    dimension = kwargs.pop('dimension', None)

    if isinstance(start, int) and isinstance(end, int):
        try:
            rng = (int(start), int(end))
        except:
            rng = None

        if not rng or len(rng) != 2:
            raise ValueError("The argument 'start=' and 'end=' to the pp_get_issue_list tag must be "
                                 "provided either in the form of an int")
    else:
        rng = (0,20)

    consensus_list = Consensus.objects.all()
    issue_list = Issue.objects.all()


    if topic and isinstance(topic, Topic): #filter by topic
        issue_list = issue_list.filter(topic__id=topic.id)
        
        
    if dimension: #filter by ranking dimension
        if dimension == "new":
            order_by = '-submit_date'
        elif dimension == "hot":
            order_by = '-interest'
        elif dimension == "cont":
            order_by = '-controversy'
        elif dimension == "top":
            order_by = '-votes'
            
        #need to filter on topic of content object and content_type.name
        if topic and isinstance(topic, Topic): consensus_list = consensus_list.filter(parent_pk=topic.pk)

        # else if there is no topic, filter by content_type issue
        else:
            c_type = ContentType.objects.get_for_model(Issue)  
            consensus_list = consensus_list.filter(content_type=c_type)
        
        issue_list = consensus_list.order_by(order_by)   

    else: #catch all for no dimension grabs new objects
        issue_list = issue_list.order_by('-submit_date')

    try: namespace['count'] = issue_list.count()
    except: namespace['count'] = 0

    issue_list = issue_list[rng[0]:rng[1]]
        
    namespace['issue_list'] = issue_list

    #issue list must be empty
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_issue_form(context, nodelist, *args, **kwargs):
    '''form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp-issue-form")
    This block tag can create or process forms either to create or to modify issues.
    Usage is as follows:

    {% pp_issue_form POST=request.POST path=request.path issue=pp_issue.issue topic=request.object %}
       Do stuff with {{ pp-issue.form }}.
    {% endpp-issue-form %}
    '''

    context.push()
    namespace = get_namespace(context)

    POST  = kwargs.get('POST', None)
    path  = kwargs.get('path', None)
    obj = kwargs.get('object',None)
    user = kwargs.get('user',None)

    if isinstance(obj, Issue):
        topic = obj.topic
        issue = obj
        namespace['contextname'] = "Edit issue " + str(issue.name)
        namespace['has_topic'] = True
            
    elif isinstance(obj,Topic):
        topic = obj 
        issue = None
        namespace['contextname'] = "Create issue on " + str(topic.text)
        namespace['has_topic'] = True
        
    else: 
        issue, topic = (None, None)
        namespace['contextname'] = "Create issue on topic of your choice"
        namespace['has_topic'] = False
            
    if POST and POST.get("form_id") == "pp_issue_form" and user is not None:
             
        if isinstance(obj, Issue):
            form = IssueForm(POST, instance=issue)
        elif isinstance(obj, Topic): 
            form = IssueForm(POST)
        else:
            form = TopicIssueForm(POST)


        if form.is_valid() and user.is_authenticated():
            issue = form.save(commit=False)
            issue.user = user
            if not isinstance(obj, Issue):
                issue.solutions = 0
                issue.arguments = 0
            issue.name = clean_html(issue.name)
            issue.text = clean_html(issue.text)
            if isinstance(topic, Topic):
                issue.topic = topic
                topic_pk = topic.pk
            else:
                topic_pk = form.cleaned_data['topics'].pk
                issue.topic = form.cleaned_data['topics']
                
            issue.save()
            contype = ContentType.objects.get_for_model(Issue)
            obj_pk  = issue.pk
            
            cons, is_new = Consensus.objects.get_or_create(content_type=contype,
                                                           object_pk=obj_pk,parent_pk=topic_pk)
                        
            if is_new: #if this is a new issue/consensus, send signal for reputation
                aso_rep_event.send(sender=issue,event_score=3, user=issue.user, dimension=ReputationDimension.objects.get('Issue Author'))
                relationship_event.send(sender=issue,obj=issue,parent=issue.topic)
            raise HttpRedirectException(HttpResponseRedirect(issue.get_absolute_url()))
        else: namespace['errors'] = form.errors
        
    else: 
        if isinstance(obj, Issue): form = IssueForm(instance=obj)
        elif isinstance(obj, Topic): form = IssueForm()
        else: form = TopicIssueForm()

        #TODO:THIS IS FOR FORMIXIN WHICH NEEDS SOME WORK        
        #form = IssueForm.create(POST, path, issue)
   # except HttpRedirectException, e:
   #     issue = e.form.instance
   #     if isinstance(topic, Topic) and isinstance(issue, Issue):
   #         issue.topic = topic
   #         issue.user = request.user            
   #         new_issue = issue.save(commit=False)
   #         new_issue.user = request.user
   #         new_issue.save()
   #     raise e
    #else:
        # Any change to the topic is ignored in this case, as well.
        # Here, the insance is not saved because saving only happens when
        # HttpRedirectException is raised, i.e. when we move on to the next page
        #if hasattr(form, 'instance') and isinstance(topic, Topic):
            #form.instance.topic = topic
            
    namespace['form'] = form
    output = nodelist.render(context)
    context.pop()

    return output

    
class TopicIssueForm(forms.ModelForm, FormMixin):
    '''
    This form is used to allow creation and modification of issue objects.  
    It extends FormMixin in order to provide a create() class method, which
    is used to process POST, path, and object variables in a consistant way,
    and in order to automatically provide the form with a form_id.
    '''

    def save(self, commit=True):
        new_issue = super(TopicIssueForm, self).save(commit=commit)
        return new_issue

    class Meta:
        model = Problem
        exclude = ('solutions','arguments','user',)
        
    #need to grab user from authenticatio
    topics = forms.ModelChoiceField(queryset=Topic.clean_objects.all())
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_issue_form")    
    name = forms.CharField(label="text", max_length=100,
              widget=forms.TextInput( 
                attrs={'size':'50', 'class':'inputText'})) 
    text = forms.CharField(widget=forms.Textarea)
