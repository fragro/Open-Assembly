from django import template
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from pirate_comments.models import Comment
from django.db import transaction
from django.middleware import csrf
from django.contrib.contenttypes.models import ContentType
from pirate_profile.models import Profile
from django.utils.encoding import smart_str
from pirate_core.helpers import clean_html
from pirate_consensus.models import Consensus, UpDownVote
from pirate_reputation.models import ReputationDimension
from pirate_sources.models import IMGSource
from django.utils.html import urlize


from markdown import markdown

import datetime
from pirate_signals.models import notification_send, relationship_event, aso_rep_event

from django.shortcuts import get_object_or_404

from pirate_core.views import HttpRedirectException, namespace_get


from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('pp_comment')


@block
def pp_comment_count(context, nodelist, *args, **kwargs): 
    context.push()
    namespace = get_namespace(context)

    object_pk = kwargs.get('object', None)
    comments = Comment.objects.all()
    count = len(list(comments.filter(object_pk=object_pk)))
    namespace['count'] = count

    output = nodelist.render(context)
    context.pop()

    return output


class DeleteForm(forms.Form):
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_delete_form")


@block
def pp_comment_delete(context, nodelist, *args, **kwargs):
    """
        This is rendered by the caching system when the user wants to delete a comment.
    """
    context.push()
    namespace = get_namespace(context)

    obj = kwargs.get('object', None)
    POST = kwargs.get('POST', None)
    user = kwargs.get('user', None)

    namespace['object_pk'] = obj.pk
    namespace['content_type'] = ContentType.objects.get_for_model(obj).pk

    if user.is_authenticated() and user == obj.user and POST is not None:
        if POST.get("form_id") == "pp_delete_form":
            if obj.is_leaf:
                obj.delete()
            else:
                obj.is_deleted = True
                obj.save()
    form = DeleteForm()

    namespace['form'] = form

    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_comment_list_get(context, nodelist, *args, **kwargs):

    """we have to render the tree html here, because recursive includes are not allowed in django templates
    this could be more efficient with pre/post order tree traversal, but for now this suffices.
    mptt and treebeard both are not designed for GAE, need a tree traversal library for non-rel"""

    context.push()
    namespace = get_namespace(context)

    object_pk = kwargs.get('object', None)
    user = kwargs.get('user', None)
    #needs request.user for reply submission
    request = kwargs.get('request', None)
    if object_pk is None:
        raise ValueError("pp_consensus_get tag requires that a consensus object be passed "
                             "to it assigned to the 'object=' argument, and that the str "
                             "be assigned the string value 'consensus.")

    comment_tree = []

    comments = Comment.objects.all()
    comments = comments.filter(object_pk=object_pk, is_root=True)
    comments = comments.order_by('-submit_date')

    for c in comments:
        if c.is_leaf:
            comment_tree.append((c, 0))
        else:
            comment_tree.append(get_children(object_pk, c))

    tree_html = render_to_comment_tree_html(comment_tree, user, request)
    tree_html = "<ul class='collapsible_comments'>" + tree_html + "</ul>"
    namespace['comments'] = tree_html
    namespace['debug_comments'] = comment_tree

    output = nodelist.render(context)
    context.pop()

    return output


def render_to_comment_tree_html(comment_tree, user, request):
    """Comment tree in form:
        c_tree = [[Comment1, [Comment1_2, Comment1_3, Comment1_4]], Comment2, Comment 3]
    must be rendered as a <ul>...<li><ul> ... <li>render_comment()</li> ... </ul> </li> </ul>"""

    ret_html = ""
    for comment in comment_tree:
        if isinstance(comment, tuple):
            ret_html += '<ul class="comment">' + render_comment(comment[0], comment[1], user, request) + "</ul>"
        elif isinstance(comment, list):
            ret_html += '<ul class="comment">' + render_comment(comment[0][0], comment[0][1], user, request) + '<ul class="comment">' + render_to_comment_tree_html(comment[1], user, request) + "</ul></ul>"

    return ret_html


#TODO: FIXED
def generate_time_string(then, now):
    time_to = abs(now - then)
    hours = time_to.seconds / 3600

    if time_to.days != 0:
        ret = str(time_to.days) + " days ago"
    elif hours == 0:
        if time_to.seconds / 60 == 0:
            ret = str(time_to.seconds) + " seconds ago"
        else:
            ret = str(time_to.seconds / 60) + " minutes ago"

    else:
        ret = str(time_to.seconds / 3600) + " hours ago"
    return " said " + ret


"""
<a href="#" class="avatar"><img src="/static/img/avatar_20x18.jpg" alt="username"></a>
    <div>
        <a href="#" class="author">Happily_siLent</a> <span class="meta">at 12:11p on 1/1/11</span>
        <p>
            Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. It has survived not only five centuries, but also the leap into electronic typesetting, remaining essentially unchanged. It was popularised in the 1960s with the release of Letraset sheets containing Lorem Ipsum passages, and more recently with desktop publishing software like Aldus PageMaker including versions of Lorem Ipsum.
        </p>
        <ul class="comment_links">
            <li><a href="#">Reply</a></li>
            <li><a href="#">Permalink</a></li>
        </ul>
    </div>

try:
    img = IMGSource.objects.get(user=user,current=True)
    ts = img.url + '=s20-c'
except:
    ts = '/static/img/avatar_20x18.jpg'

html = "<a href='/user_profile.html" + "?_t=" + str(content_type.pk) + "&_o=" + str(comment_obj.user.pk) + "'" + ' class="avatar"><img src="' + ts + '" alt="' + str(user.username) + '"></a>'
html += "<div id='comment" + str(comment_obj.id) + "'>"
html += "<a href='/user_profile.html" + "?_t=" + str(content_type.pk) + "&_o=" + str(comment_obj.user.pk) + "'" + ' class="author">' + str(user.username) + '</a> <span class="meta">' + generate_time_string(comment_obj.submit_date, datetime.datetime.now()) +  '</span><p>'
html += smart_str(comment_obj.text, encoding='utf-8', strings_only=False, errors='strict') + '</p>'
html += '<ul class="comment_links">' + '<li>' + "<a href='javascript:;' onmousedown=" + "'toggleSlide(" + '"add_reply' + str(comment_obj.id) + '"' + ");'>reply</a>" + '</li>' + '<li>' + "<a href='/" + path + "'>permalink</a>" + '</li>'
html += '</ul>'
html += "<div id='add_reply" + str(comment_obj.id) + "' style='display:none; overflow:hidden; height:250px;'><form id='add_reply_form" + str(comment_obj.id) +"' method='post' action=''><div style='display:none'><input type='hidden' name='csrfmiddlewaretoken' value='" + str(csrf.get_token(request)) + "' /><input id='reply_to_object' type='hidden' name='reply_to_object' value='" + str(comment_obj.id)+ "'/></div>" + str(form.as_p()) + "<input type='submit' class='button green' value='Submit Comment'></form></div></div>"
html+= "</div>"
"""


def render_comment(comment_obj, count, user, request):
    #ok this is as ugly as it gets, but there's little other ways to generate this html that I am aware of
    content_type = ContentType.objects.get_for_model(comment_obj.user)
    path = "detail.html?_t=" + str(comment_obj.content_type.pk) + "&_o=" + str(comment_obj.object_pk)
    form = ReplyForm(initial={'is_root': False, 'is_leaf': True, 'content_type': comment_obj.content_type,
            'object_pk': comment_obj.object_pk, 'reply_to': comment_obj, 'submit_date': datetime.datetime.now(), 'user': user})

    """returns the relevant html for a single atomic comment given the comment object"""
    try:
        img = IMGSource.objects.get(object_pk=comment_obj.user.id, current=True)
        ts = img.url + '=s20-c'
    except:
        ts = '/static/img/avatar_20x18.jpg'
    html = "<a href='/user_profile.html" + "?_t=" + str(content_type.pk) + "&_o=" + str(comment_obj.user.pk) + "'" + ' class="avatar"><img src="' + ts + '" alt="' + str(user.username) + '"></a>'
    html += "<li id='comment" + str(comment_obj.id) + "'>"
    html += "<a href='/user_profile.html" + "?_t=" + str(content_type.pk) + "&_o=" + str(comment_obj.user.pk) + "'" + ' class="author">' + str(comment_obj.user.username) + '</a> <span class="meta">' + generate_time_string(comment_obj.submit_date, datetime.datetime.now()) +  '</span><p>'
    text = markdown(comment_obj.text, safe_mode=True)
    html += smart_str(text, encoding='utf-8', strings_only=False, errors='strict') + '</p>'

    if user.is_authenticated():
        html += '<ul class="comment_links">' + '<li>' + "<a href='javascript:;' onmousedown=" + "'toggleSlide(" + '"add_reply' + str(comment_obj.id) + '"' + ");'>reply</a>" + '</li>' + '<li>' + "<a href='/" + path + + str(comment_obj.id) + "'>permalink</a>" + '</li>'
    else:
        html += '<ul class="comment_links">' + '<li>' + "<a href='/" + path + "&_i=s'>reply</a>" + '</li>' + '<li>' + "<a href='/" + path + "&_c=comment" + str(comment_obj.id) + "'>permalink</a>" + '</li>'
    if comment_obj.user == user:
        html += '<li>' + "<a href='javascript:;' onmousedown=" + "'toggleSlide(" + '"edit_reply' + str(comment_obj.id) + '"' + ");'>edit</a>" + '</li>'
    html += '</ul>'
    html += '<p>'
    if user.is_authenticated():
        html += "<div class='reply_comment' id='add_reply" + str(comment_obj.id) + "' style='display:none; overflow:hidden; height:290px;width:100%;'><form id='add_reply_form" + str(comment_obj.id) +"' method='post' action=''><div style='display:none'><input type='hidden' name='csrfmiddlewaretoken' value='" + str(request.COOKIES.get('csrftoken')) + "' /><input id='reply_to_object' type='hidden' name='reply_to_object' value='" + str(comment_obj.id)+ "'/></div>" + str(form.as_p()) + "<input type='submit' class='button' value='Submit'></form></div>"
    if comment_obj.user == user:
        editform = CommentForm(instance=comment_obj)
        html += "<div class='reply_comment' id='edit_reply" + str(comment_obj.id) + "' style='display:none; overflow:hidden; height:290px;width:100%;'><form id='add_reply_form" + str(comment_obj.id) +"' method='post' action=''><div style='display:none'><input type='hidden' name='csrfmiddlewaretoken' value='" + str(request.COOKIES.get('csrftoken')) + "' /><input id='edit_object' type='hidden' name='edit_object' value='" + str(comment_obj.id)+ "'/>" + '<input type="hidden" name="form_id" value="pp_comment_form' +  str(comment_obj.id) + '" id="id_form_id"/>' + "</div>" + str(editform.as_p()) + "<input type='submit' class='button' value='Submit'></form></div>"
    html += '</p>'
    html += "</li>"
    return urlize(html, trim_url_limit=30, nofollow=True)

    #return "<div id='comment" + str(comment_obj.id) + "'> <div class='comment_user'> <a href='/user_profile.html" + "?_t=" + str(content_type.pk) + "&_o=" + str(comment_obj.user.pk) + "'>" + str(comment_obj.user.username)+ "</a>" + generate_time_string(comment_obj.submit_date, datetime.datetime.now()) + ":</div><div>" + smart_str(comment_obj.text, encoding='utf-8', strings_only=False, errors='strict') +"</div><div class='comment_reply'>" + " <a href='javascript:;' onmousedown=" + "'toggleSlide(" + '"add_reply' + str(comment_obj.id) + '"' + ");'>reply</a> <a href='/" + path + "'>permalink</a><div id='add_reply" + str(comment_obj.id) + "' style='display:none; overflow:hidden; height:250px;'><form id='add_reply_form" + str(comment_obj.id) +"' method='post' action=''><div style='display:none'><input type='hidden' name='csrfmiddlewaretoken' value='" + str(csrf.get_token(request)) + "' /><input id='reply_to_object' type='hidden' name='reply_to_object' value='" + str(comment_obj.id)+ "'/></div>" + str(form.as_p()) + "<input type='submit' class='button green' value='Submit Comment'></form></div></div></div>"


def get_children(object_pk, cur_comment):
    get_list = []
    comments = Comment.objects.all()
    comments = comments.filter(object_pk=object_pk, is_root=False, reply_to=cur_comment)
    for c in comments:
        if c.is_leaf:
            get_list.append((c, 0))
        else:
            get_list.append(get_children(object_pk, c))
    return [(cur_comment, len(comments)), get_list]


@block
def pp_comment_form(context, nodelist, *args, **kwargs):
    '''
    This block tag can create or process forms either to create or to modify issues.
    Usage is as follows:

    {% pp_comment_form POST=request.POST object=request.object user=request.user %}
       Do stuff with {{ pp-comment.form }}.
    {% endpp_comment_form %}
    '''

    context.push()
    namespace = get_namespace(context)

    POST = kwargs.get('POST', None)
    reply_to = kwargs.get('object', None)
    user = kwargs.get('user', None)
    comment = kwargs.get('edit', None)

    if comment is not None:
        if POST and POST.get("form_id") == "pp_edit_form":
            form = CommentForm(POST, instance=comment)
            if form.is_valid():
                comment.text = clean_html(form.cleaned_data['text'])
                comment.save()
        else:
            form = CommentForm(instance=comment)

        namespace['object_pk'] = comment.pk
        namespace['content_type'] = ContentType.objects.get_for_model(comment).pk

    elif POST and POST.get("form_id") == "pp_comment_form":
        form = CommentForm(POST) if comment is None else CommentForm(POST, instance=comment)
        if form.is_valid():
                newcomment = form.save(commit=False)
                newcomment.user = user
                c_type = ContentType.objects.get_for_model(reply_to.__class__)
                newcomment.content_type = c_type
                newcomment.object_pk = reply_to.pk
                newcomment.text = clean_html(newcomment.text)
                newcomment.reply_to = None
                newcomment.is_leaf = True
                newcomment.submit_date = datetime.datetime.now()
                newcomment.is_root = True
                newcomment.save()
                namespace['object_pk'] = newcomment.pk
                namespace['content_type'] = ContentType.objects.get_for_model(newcomment).pk
                cvt = ContentType.objects.get_for_model(UpDownVote)
                cons, is_new = Consensus.objects.get_or_create(content_type=c_type,
                                    object_pk=newcomment.pk,
                                    vote_type=cvt,
                                    parent_pk=reply_to.pk)
                notification_send.send(sender=newcomment, obj=newcomment, reply_to=newcomment.content_object)
                relationship_event.send(sender=newcomment, obj=newcomment, parent=newcomment.content_object)
                aso_rep_event.send(sender=newcomment.user, event_score=1, user=newcomment.content_object.user,
                    initiator=newcomment.user, dimension=ReputationDimension.objects.get("comment"), related_object=newcomment)
            #raise HttpRedirectException(HttpResponseRedirect(newcomment.get_absolute_url()))
                form = CommentForm()
        else:
            namespace['errors'] = form.errors

    elif POST and POST.get("form_id") == "pp_reply_form":
        form = ReplyForm(POST) if comment is None else ReplyForm(POST, instance=comment)
        if form.is_valid():
            newcomment = form.save(commit=False)
            newcomment.user = user
            newcomment.content_type = reply_to.content_type
            newcomment.object_pk = reply_to.object_pk
            newcomment.reply_to = Comment.objects.get(pk=reply_to.pk)
            newcomment.reply_to.is_leaf = False
            newcomment.reply_to.save()
            newcomment.text = clean_html(newcomment.text)
            newcomment.is_leaf = True
            newcomment.is_root = False
            newcomment.submit_date = datetime.datetime.now()
            newcomment.save()
            namespace['object_pk'] = newcomment.pk
            namespace['content_type'] = ContentType.objects.get_for_model(newcomment).pk
            cvt = ContentType.objects.get_for_model(UpDownVote)
            cons, is_new = Consensus.objects.get_or_create(content_type=reply_to.content_type,
                                    object_pk=newcomment.pk,
                                    vote_type=cvt,
                                    parent_pk=reply_to.object_pk)
            if comment is None:
                #if comment is new and not editted
                notification_send.send(sender=newcomment, obj=newcomment, reply_to=newcomment.reply_to)
                relationship_event.send(sender=newcomment, obj=newcomment, parent=newcomment.reply_to)
                aso_rep_event.send(sender=newcomment.user, event_score=1, user=newcomment.reply_to.user,
                    initiator=newcomment.user, dimension=ReputationDimension.objects.get("comment"), related_object=newcomment)
        #raise HttpRedirectException(HttpResponseRedirect(newcomment.get_absolute_url()))
        form = CommentForm()
    else:
        form = CommentForm() if comment is None else CommentForm(instance=comment)

    namespace['form'] = form
    output = nodelist.render(context)
    context.pop()

    return output


class CommentForm(forms.ModelForm):
    '''
    This form is used to allow creation and modification of comment objects.  
    It extends FormMixin in order to provide a create() class method, which
    is used to process POST, path, and object variables in a consistant way,
    and in order to automatically provide the form with a form_id.
    '''

    def save(self, commit=True):
        new_comment = super(CommentForm, self).save(commit=commit)
        return new_comment

    class Meta:
        model = Comment
        exclude = ('user','object_pk','content_type','reply_to','submit_date', 'is_leaf','is_root', 'content_object')
    #need to grab user from authenticatio
    #form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_comment_form")
    text = forms.CharField(widget=forms.Textarea, label="")

class ReplyForm(forms.ModelForm):
    '''
    This form is used to allow creation and modification of comment objects.  
    It extends FormMixin in order to provide a create() class method, which
    is used to process POST, path, and object variables in a consistant way,
    and in order to automatically provide the form with a form_id.
    '''

    def save(self, commit=True):
        new_comment = super(ReplyForm, self).save(commit=commit)
        return new_comment

    class Meta:
        model = Comment
        exclude = ('user','object_pk','content_type','reply_to','submit_date', 'is_leaf','is_root', 'content_object')
    #need to grab user from authenticatio
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_reply_form")
    text = forms.CharField(widget=forms.Textarea,label="")


