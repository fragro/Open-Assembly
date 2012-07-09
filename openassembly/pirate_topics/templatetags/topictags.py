from django import template
from django import forms

from pirate_permissions.models import Permission, PermissionsGroup

import re
from django.contrib.contenttypes.models import ContentType

from markitup.widgets import MarkItUpWidget

from pirate_topics.models import Topic, MyGroup, GroupSettings, get_root
from pirate_core.views import namespace_get

from django.utils.html import urlize

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

from pirate_forum.models import get_rangelist


get_namespace = namespace_get('pp_topic')


@block
def pp_get_topic_if_content(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    obj = kwargs.pop('object', None)

    ctype_obj = ContentType.objects.get_for_model(obj)
    ctype = ContentType.objects.get_for_model(Topic)

    ret = None
    if ctype == ctype_obj:
        #if object is a topic
        ret = obj
    elif obj.parent is not None:
        ret = obj.parent

    namespace['object'] = ret
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_get_root(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)
    root = kwargs.pop('object', None)
    root = get_root(root)
    namespace['root'] = root
    #except:
    #    namespace['root'] = None
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_check_siblings(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)
    root = kwargs.pop('object', None)
    user = kwargs.pop('user', None)

    topics = Topic.objects.filter(parent=root)
    in_child = False
    group = None
    for i in topics:
        try:
            mygroup = MyGroup.objects.get(topic=i, user=user)
            in_child = True
            group = i
            break
        except:
            pass

    namespace['ingroup'] = in_child
    namespace['group'] = group
    #except:
    #    namespace['root'] = None
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_get_topic(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)
    obj = kwargs.pop('object', None)
    object_pk = kwargs.pop('object_pk', None)
    topicname = kwargs.pop('topicname', None)

    try:
        if topicname is not None:
            try:
                topic = Topic.objects.get(summary=topicname)
            except:
                topic = None
        else:
            topic = None
        parent = None
        if obj is not None:
            try:
                if obj.get_child_blob_key():
                    parent = obj
            except:
                try:
                    if obj.parent.summary != '__NULL__':
                        parent = obj.parent
                    else:
                        parent = obj
                except:
                    pass

        if object_pk is not None:
            top = Topic.objects.get(pk=object_pk)
        else:
            top = None
    except:
        parent = None
        topic = None
        top = None

    namespace['parent'] = parent
    namespace['topic'] = topic
    namespace['object'] = top

    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_add_mygroup(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    topic = kwargs.pop('topic', None)
    user = kwargs.pop('user', None)

    mygroup, is_new = MyGroup.objects.get_or_create(user=user, topic=topic)
    topic.group_members += 1
    topic.save()

    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_get_topic_hierarchy(context, nodelist, *args, **kwargs):
    """
    This block tag will grab the parent of a topic. Each Topic object contains
    a parent or if a root node contains a null value. In this case the object returned
    is either that parent, or the None object.

    {% pp_get_topic_hierarchy topic = object %}
       Do stuff with {{ pp_topic.hierarchy }}
    {% endpp_get_topic_hierarchy %}
    """

    context.push()
    namespace = get_namespace(context)

    root = kwargs.pop('topic', None)

    if root != None and isinstance(root, Topic):

        hierarchy = []
        hierarchy.insert(0, root)

        parent = root.parent

        while parent != None and parent.summary != '__NULL__':
            parent = root.parent
            hierarchy.insert(0, parent)
    else:
        hierarchy = None

    namespace['hierarchy'] = hierarchy
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_get_topic_list(context, nodelist, *args, **kwargs):
    """
    This block tag will grab a list of topics. This also takes an argument 'topic'
    allowing the template to specify a root topic, in which case each child of this topic
    will be included in 'children'.

    In order to generate a url that will provide rng information to this tag via
    request.range, use a url tag of the following form:

    {% url pp-page template="filename.html" start=0 end=20 %}

    In this way, the tag can be invoked as follows:

    {% pp_get_topic_list range=request.range topic = root_topic %}
       Do stuff with {{ pp_topic.topic_list }}
    {% endpp_get_topic_list %}

    >>> from pirate_issues.models import Topic
    >>> topic = Topic(text = "newtopic")
    >>> topic.save()
    >>> topic2 = Topic(text = "childtopic", parent = topic)
    >>> topic2.save()
    >>> topic3 = Topic(text = "nexttopic", parent = topic2)
    >>> Topic.objects.all()
    [<Topic: taxes>, <Topic: debt>, <Topic: A test topic.>, <Topic: newtopic>, <Topic: childtopic>]
    >>> Topic.clean_objects.filter(parent = topic)
    [<Topic: childtopic>]
    >>> Topic.clean_objects.filter(parent = Topic.objects.null_dimension())
    []
    """

    context.push()
    namespace = get_namespace(context)
    root = kwargs.pop('topic', None)

    topic_list = []

    if root != None and isinstance(root, Topic):
        topic_list = Topic.objects.filter(parent=root).order_by('-children')
    else:
        topic_list = Topic.objects.filter(parent=Topic.objects.null_dimension()).order_by('-children')

    namespace['topic_list'] = topic_list
    namespace['count'] = topic_list.count()
    output = nodelist.render(context)
    context.pop()

    return output


@block
def oa_ingroup(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    obj = kwargs.get('object', None)
    user = kwargs.get('user', None)

    try:
        in_group = MyGroup.objects.get(topic=obj, user=user)
        namespace['in_group'] = True
    except:
        namespace['in_group'] = False

    output = nodelist.render(context)
    context.pop()

    return output


@block
def oa_mygroup_users(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    obj = kwargs.get('object', None)
    start = kwargs.get('start', None)
    end = kwargs.get('end', None)

    try:
        mygroups = MyGroup.objects.filter(topic=obj)
        cnt = mygroups.count()

    except:
        mygroups = None
        cnt = 0

    if start is not None and end is not None and mygroups is not None:
        mygroups = mygroups[int(start):int(end)]

    namespace['rangelist'] = get_rangelist(start, end, cnt)

    namespace['groups'] = mygroups
    namespace['count'] = cnt

    output = nodelist.render(context)
    context.pop()

    return output


@block
def oa_get_group_settings(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    obj = kwargs.get('object', None)

    try:
        if obj is not None:
            s, is_new = GroupSettings.objects.get_or_create(topic=obj)
        else:
            s = None
    except:
        s = None

    namespace['settings'] = s

    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_mygroups(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    start = kwargs.get('start', None)
    end = kwargs.get('end', None)

    if user.is_authenticated():
        mygroups = MyGroup.objects.filter(user=user)[int(start):int(end)]

        namespace['mygroups'] = mygroups

        namespace['count'] = mygroups.count()
        namespace['half'] = (mygroups.count() / 2) + 1

    output = nodelist.render(context)
    context.pop()

    return output


_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')
def _slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    From Django's "django/template/defaultfilters.py".
    """
    import unicodedata
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)


@block
def pp_getcreate_setting(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    topic = kwargs.get('topic', None)
    if topic is not None:
        settings, is_new = GroupSettings.objects.get_or_create(topic=topic)
    else:
        settings = None
    namespace['settings'] = settings

    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_topic_form(context, nodelist, *args, **kwargs):
    '''
    This block tag can create or process forms eitfrom genericview.views import HttpRedirectException, namespace_gether to create or to modify arguments.
    Usage is as follows:

    {% pp_topic_form POST=request.POST path=request.path topic=pp_topic.topic root=some_topic %}
       Do stuff with {{ pp_topic.form }}.
    {% endpp_topic_form %}
    '''
    context.push()
    namespace = get_namespace(context)

    POST = kwargs.get('POST', None)
    topic = kwargs.get('topic', None)
    root = kwargs.get('root', Topic.objects.null_dimension())
    user = kwargs.get('user', None)

    if POST and (POST.get("form_id") == "create_group" or POST.get("form_id") == "pp_edittopic_form")and user is not None:
        form = TopicForm(POST) if topic is None else EditTopicForm(POST, instance=topic)
        if form.is_valid():
            new_topic = None
            if topic is not None:
                new_topic = form.save(commit=False)
                new_topic.is_featured = False
                new_topic.description = urlize(new_topic.description, trim_url_limit=30, nofollow=True)
                new_topic.slug = _slugify(new_topic.summary)
                #let's see if there are any groups with this shortname or full name
            #raise HttpRedirectException(HttpResponseRedirect("/topics.html"))
            if topic is None:
                new_topic = form.save(commit=False)
                ctype = ContentType.objects.get_for_model(new_topic)
                #create Facilitator permissions for group creator
                new_topic.save()
                new_topic.group_members = 1
                new_topic.save()
                perm_group, is_new = PermissionsGroup.objects.get_or_create(name="Facilitator", description="Permission group for Facilitation of Online Working Groups")
                perm = Permission(user=user, name='facilitator-permission', content_type=ctype,
                            object_pk=new_topic.pk, permissions_group=perm_group, component_membership_required=True)
                perm.save()
                mg, is_new = MyGroup.objects.get_or_create(topic=new_topic, user=user)
            if new_topic is not None:
                ctype = ContentType.objects.get_for_model(new_topic)
                namespace['content_type'] = ctype.pk
                namespace['object_pk'] = new_topic.pk
                namespace['complete'] = True
                if root and isinstance(root, Topic):
                    new_topic.parent = root
                    new_topic.save()
                else:
                    new_topic.parent = Topic.objects.null_dimension()
                    new_topic.save()

        else:
            namespace['errors'] = form.errors
    else:
        form = TopicForm() if topic is None else EditTopicForm(instance=topic)

    namespace['form'] = form
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_setting_form(context, nodelist, *args, **kwargs):
    '''
    This block tag can create or process forms eitfrom genericview.views import HttpRedirectException, namespace_gether to create or to modify arguments.
    Usage is as follows:

    {% pp_topic_form POST=request.POST path=request.path topic=pp_topic.topic root=some_topic %}
       Do stuff with {{ pp_topic.form }}.
    {% endpp_topic_form %}
    '''
    context.push()
    namespace = get_namespace(context)

    POST = kwargs.get('POST', None)
    setting = kwargs.get('object', None)

    if POST and POST.get("form_id") == "oa_group_settings_form":
        form = SettingsForm(POST) if setting is None else SettingsForm(POST, instance=setting)
        form.save()
        namespace['complete'] = True
    else:
        form = SettingsForm() if setting is None else SettingsForm(instance=setting)

    namespace['form'] = form
    output = nodelist.render(context)
    context.pop()

    return output


class InviteForm(forms.ModelForm):

    def save(self, commit=True):
        newo = super(SettingsForm, self).save(commit=commit)
        return newo

    class Meta:
        model = GroupSettings
        exclude = ('topic')

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="oa_group_settings_form")

streamproviderchoices = (
    ('N', 'None'),
    ('U', 'UStream'),
    ('L', 'Livestream'),
)


class SettingsForm(forms.ModelForm):

    def save(self, commit=True):
        newo = super(SettingsForm, self).save(commit=commit)
        return newo

    class Meta:
        model = GroupSettings
        exclude = ('topic')

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="oa_group_settings_form")
    stream_provider = forms.ChoiceField(choices=streamproviderchoices)


class TopicForm(forms.ModelForm):

    def save(self, commit=True):
        newo = super(TopicForm, self).save(commit=commit)
        return newo

    class Meta:
        model = Topic
        exclude = ('parent', 'children', 'is_featured', 'slug', 'group_members', 'decisions', 'solutions')

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="create_group")
    summary = forms.CharField(max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}),  label="Comprehensive Name of the Group")
    shortname = forms.CharField(max_length=23,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}), label="Short Name (20 Characters or Less)")
    more_info = forms.CharField(required=False, max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}), label="Link to Group Website")
    description = forms.CharField(widget=forms.Textarea, label="Group Description")
    location = forms.CharField(label="Location", max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}), required=False)


#hack to get around markitup selecting divs and
#applying itself twice when two forms are on the same page
class EditTopicForm(forms.ModelForm):

    def save(self, commit=True):
        newo = super(EditTopicForm, self).save(commit=commit)
        return newo

    class Meta:
        model = Topic
        exclude = ('parent', 'children', 'is_featured', 'slug', 'group_members', 'decisions', 'solutions')

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_topic_form")
    summary = forms.CharField( max_length=100,
              widget=forms.TextInput(
                attrs={'size':'50', 'class':'inputText'}),label="Comprehensive Name of the Group")
    shortname = forms.CharField( max_length=20,
              widget=forms.TextInput(
                attrs={'size':'50', 'class':'inputText'}),label="Short Name (20 Characters or Less)")
    more_info = forms.CharField(required=False, max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}),label="Link to Group Website") 
    description = forms.CharField(widget=forms.Textarea,label="Edit Description")
    location = forms.CharField(label="Location", max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}),required=False)
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_edittopic_form")
