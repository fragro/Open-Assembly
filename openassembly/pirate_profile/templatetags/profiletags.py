from django import template
from django import forms
from django.http import HttpResponseRedirect
import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from tagging.models import Tag, TaggedItem
from pirate_profile.models import Profile
from pirate_core.helpers import clean_html
from pirate_sources.models import IMGSource
from google.appengine.api import images

from pirate_core import HttpRedirectException, namespace_get, FormMixin

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('pp_profile')


@block
def pp_get_user_profile(context, nodelist, *args, **kwargs):
    '''
    This block tag can create or process forms to get tags.
    Usage is as follows:
    {% pp_get_user_profile user=requet.object %}
       Do stuff with {{ pp_profile.user }} and {{ pp_profile.profile }}.
    {% endpp_get_user_profile %}
    '''
    
    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)

    if user is not None and isinstance(user, User):
        try:
            profile = Profile.objects.get(user=user)
        except:
            profile = None
    elif user is not None and isinstance(user, Profile):
        profile = user
        user = profile.user
    else:
        profile = None
        user = None

    namespace['user'] = user
    namespace['profile'] = profile
    output = nodelist.render(context)
    context.pop()
    return output

@block
def pp_avatar_thumbnail(context, nodelist, *args, **kwargs):
    '''
    This block tag can create or process forms either to create or to modify arguments.
    Usage is as follows:

    {% pp_profile_form POST=request.POST object=request.object %}
       Do stuff with {{ pp_profile.form }}.
    {% endpp_profile_form %}
    '''

    context.push()
    namespace = get_namespace(context)
    pk = kwargs.get('pk', None)
    try:
        img = IMGSource.objects.get(pk=pk)
    except:
        img = '/static/img/avatar_20x18.jpg'

    namespace['avatar_url'] = img.url + '=s20-c'
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_profile_form(context, nodelist, *args, **kwargs):
    '''
    This block tag can create or process forms either to create or to modify arguments.
    Usage is as follows:

    {% pp_profile_form POST=request.POST object=request.object %}
       Do stuff with {{ pp_profile.form }}.
    {% endpp_profile_form %}
    '''
    
    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user',None)
    profile = kwargs.get('profile',None)
    POST = kwargs.get('POST',None)

    if POST and POST.get("form_id") == "pp_profile_form":
        if user.is_authenticated:
            if profile is not None and isinstance(profile, Profile): form = ProfileForm(POST, instance=profile)
            else: form = ProfileForm(POST)       
            #new_arg = form.save(commit=False)
            if form.is_valid():
                new_profile=form.save(commit=False)
                new_profile.user = user
                new_profile.bio = clean_html(new_profile.bio)
                new_profile.save()
                raise HttpRedirectException(HttpResponseRedirect(new_profile.get_absolute_url()))
            else:
                namespace['errors'] = form.errors
        else: 
            raise HttpRedirectException(HttpResponseRedirect('/register.html'))
    else:
        if profile is not None and isinstance(profile, Profile): form = ProfileForm(instance=profile)
        else: form = ProfileForm()

    namespace['form'] = form
    output = nodelist.render(context)
    context.pop()

    return output    


@block
def pp_get_avatar(context, nodelist, *args, **kwargs):
    
    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    
    try: 
        img = IMGSource.objects.get(object_pk=user.pk,current=True)
        url = img.url + '=s180-c'
        thumbnail = img.url + '=s70-c'
        thumbnail_small = img.url + '=s20-c'
        has_avatar = True
    except:
        url = '/static/img/avatar_180x160.jpg' 
        thumbnail = '/static/img/avatar_70x60.jpg' 
        thumbnail_small = '/static/img/avatar_20x18.jpg'
        has_avatar = False
        
    #get_serving_url will serve up full size images as well as transformed images

    namespace['avatar_url'] = url
    namespace['thumbnail'] = thumbnail
    namespace['thumbnail_small'] = thumbnail_small
    namespace['has_avatar'] = has_avatar
    output = nodelist.render(context)
    context.pop()

    return output  

    
class ProfileForm(forms.ModelForm):

    def save(self, commit=True):
        new_prof = super(ProfileForm, self).save(commit=commit)
        return new_prof

    class Meta:
        model = Profile
        exclude = ('user','submit_date')

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_profile_form")
    birth_date = forms.DateField(widget=forms.DateInput,required=False)
    bio = forms.CharField(widget=forms.Textarea, label="Who are you?",required=False)
