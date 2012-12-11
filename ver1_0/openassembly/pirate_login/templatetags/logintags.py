from django import template
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
import datetime

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from pirate_core import HttpRedirectException, namespace_get
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate, login
from django.core.validators import validate_email
from tracking.models import utils, Visitor

from captcha.fields import ReCaptchaField

from pirate_topics.models import MyGroup

from pirate_forum.models import View

from settings import DOMAIN_NAME

from oa_verification.models import Referral

from pirate_login.models import Login, Register
from pirate_social.models import Location

from oa_verification.models import EmailVerification
import datetime, random, sha
from django.core.mail import send_mail

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)


'''
This file contains all of the tags that pertain to User/Login objects
'''
# this function assignment lets us reuse the same code block a bunch of places
get_namespace = namespace_get('pp_login')


class KeyGenerator(forms.Form):
    """Form for generating a new key for registration."""
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_key_generator")
    user = forms.CharField(label=_(u'Username'))


@block
def pp_last_visit(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    obj = kwargs.get('object', None)

    if obj is not None:
        obj_pk = obj.pk
    else:
        obj_pk = None

    view = View.objects.filter(user=user, object_pk=obj_pk, rendertype='list')

    num = view.count()

    namespace['num_since_last_visit'] = num
    output = nodelist.render(context)
    context.pop()

    return output


@block
def is_online(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    timeout = kwargs.get('timeout', None)

    """
    Retrieves only visitors who have been active within the timeout
    period.
    """
    if not timeout:
        timeout = utils.get_timeout()

    now = datetime.datetime.now()
    cutoff = now - datetime.timedelta(minutes=timeout)

    visit = Visitor.objects.filter(user=user, last_update__gte=cutoff)
    online = visit.count() > 0
    namespace['online'] = online
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_generate_key(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    POST = kwargs.get('POST', None)

    if POST is not None and POST.get("form_id") == "pp_key_generator":
        form = KeyGenerator(POST)
        if form.is_valid():
            u_key = form.cleaned_data['user']
            try:
                user = User.objects.get(username=u_key)
                if user.is_active:
                    namespace['errors'] = 'User already active! Login to start browsing.'
                else:
                    salt = sha.new(str(random.random())).hexdigest()[:5]
                    activation_key = sha.new(salt + user.username).hexdigest()
                    key_expires = datetime.datetime.today() + datetime.timedelta(2)

                    #delete expired email verification
                    old_ver = EmailVerification.objects.get(user=user)
                    old_ver.delete()
                                                                                                                      
                    new_profile = EmailVerification(user=user,
                                              activation_key=activation_key,
                                              key_expires=key_expires)
                    new_profile.save()
                                                                                                           
                    email_subject = 'OpenAssembly account confirmation'
                    email_body = "Hello, %s, and thanks for signing up for an Open Assembly account!\n\nTo activate your account, click this link within 48 hours:\n\n%sconfirm/%s/" % (
                        user.username, DOMAIN_NAME,
                        new_profile.activation_key)
                    send_mail(email_subject,
                              email_body,
                              'fragro@gmail.com',
                              [user.email])
                    namespace['errors'] = 'New Confirmation Email Sent! Check Your Mail Soon.'

            except:
                namespace['errors'] = 'Username not found.'
        else:
           form = KeyGenerator(POST)
           namespace['errors'] = form.errors

    else:
        form = KeyGenerator()

    namespace['form'] = form
    output = nodelist.render(context)
    context.pop()    

    return output


@block    
def pp_user_registration_form(context, nodelist, *args, **kwargs):
    '''form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_user_registration_form")
    This block tag can create or process forms either to create or to modify issues.
    Usage is as follows:

    {% pp_user_login_form request=request return_path=request.MATH.PATH_INFO return_query=request.META.QUERY_STRING %}
       Do stuff with {{ pp_login.form }}.
    {% endpp_user_login_form%}
    '''
    context.push()
    namespace = get_namespace(context)

    request = kwargs.get('request')
    dimension=kwargs.get('dimension', None)
    return_path= kwargs.get('return_path')
    return_query= kwargs.get('return_query')
    returnurl = kwargs.get('returnurl') #this is for register.html:
    user = kwargs.get('user', None)

    if request is not None: 
        POST = request.POST
    else:
        raise ValueError("Tag pp_user_login_form must contain the argument 'request=request'")

    if POST and POST.get("form_id") == "pp_user_registration_form":
        if user.is_authenticated():
            form = RegisterForm(POST)
            namespace['errors'] = "You are already logged in. Log out and try again."
        else:
            try:
                form = RegisterForm(POST)
                if form.is_valid():
                    new_user = form.save()
                    if new_user.password1 == new_user.password2:
                        #check to see if there are other users with this name
                        try:
                            ui = User.objects.get(username__iexact=new_user.name)
                            namespace['errors'] = "Sorry that username is taken already, please pick another."
                        except:
                            user = User.objects.create_user(new_user.name, new_user.email, new_user.password1)
                            user.is_active = False
                            user.save()
                            #set user location
                            user = authenticate(username=new_user.name, password=new_user.password1)

                            if user is not None:
                                #if this is a referred user
                                if dimension is not None:
                                    #try:
                                    ref = Referral.objects.get(key=dimension, accepted=False)
                                    ref.referred_user = user
                                    ref.accepted_dt = datetime.datetime.now()
                                    ref.accepted = True
                                    ref.save()
                                    user.is_active = True
                                    user.save()
                                    login(request, user)

                                    if ref.topic is not None:
                                        mg, is_new = MyGroup.objects.get_or_create(user=user, topic=ref.topic)
                                        ref.topic.group_members += 1
                                        ref.topic.save()
                                    namespace['success'] = 'Account created and group joined!'
                                    #except:
                                    #    namespace['errors'] = "Illegal Referral Key"
                                else:
                                    salt = sha.new(str(random.random())).hexdigest()[:5]
                                    activation_key = sha.new(salt + user.username).hexdigest()
                                    key_expires = datetime.datetime.today() + datetime.timedelta(2)

                                    new_profile = EmailVerification(user=user,
                                                              activation_key=activation_key,
                                                              key_expires=key_expires)
                                    new_profile.save()

                                    email_subject = 'OpenAssembly account confirmation'
                                    email_body = "Hello, %s, and thanks for signing up for an Open Assembly account!\n\nTo activate your account, click this link within 48 hours:\n\n%sconfirm/%s/" % (
                                        user.username, DOMAIN_NAME,
                                        new_profile.activation_key)
                                    send_mail(email_subject,
                                              email_body,
                                              'fragro@gmail.com',
                                              [user.email])
                                    namespace['success'] = 'Check your email for confirmation!'
                    else:
                        namespace['errors'] = "Passwords are not the same. Try again."
            except HttpRedirectException, e:
                raise e
    else:
        form = RegisterForm()

    namespace['form'] = form
    output = nodelist.render(context)
    context.pop()

    return output


class RegisterForm(forms.ModelForm):
    def save(self, commit=True):
        new_user = super(RegisterForm, self).save(commit=False)
        return new_user

    class Meta:
        model = Register

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_user_registration_form")
    password1 = forms.CharField(label=_(u'Password'), widget=forms.PasswordInput(render_value=False))
    password2 = forms.CharField(label=_(u'Password Check'), widget=forms.PasswordInput(render_value=False))
    email = forms.CharField(label=_(u'Email'), validators=[validate_email])
    captcha = ReCaptchaField()


@block
def pp_user_login_form(context, nodelist, *args, **kwargs):
    '''form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_user_login_form")
    This block tag can create or process forms either to create or to modify issues.
    Usage is as follows:

    {% pp_user_login_form request=request return_path=request.MATH.PATH_INFO return_query=request.META.QUERY_STRING %}
       Do stuff with {{ pp_login.form }}.
    {% endpp_user_login_form%}
    '''
    context.push()
    namespace = get_namespace(context)

    request = kwargs.get('request')
    dimension = kwargs.get('dimension')

    if request is not None:
        POST = request.POST
    else:
        raise ValueError("Tag pp_user_login_form must contain the argument 'request=request'")
    #returnurl = returnurl.replace('&_i=s','').replace('?_i=s','')

    if POST and POST.get("form_id") == "pp_user_login_form":
        #if return_path != None: namespace['display'] = 'display:inline;' #for ajax, this changes the DIV to stay open if the user login info is incorrect
        form = LoginForm(POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data['name'], password=form.cleaned_data['password'])
            #user = User.objects.get(username=new_user.name)
            log_file = form.save()
            log_file.password = None
            log_file.ip = request.META.get('REMOTE_ADDR')
            log_file.created_dt = datetime.datetime.now()
            log_file.save()
            if user is not None:
                if user.is_active:
                    login(request, user)
                    namespace['complete'] = True
                    #check the user's current location
                    if dimension is not None:
                        try:
                            ref = Referral.objects.get(key=dimension, accepted=False)
                            ref.referred_user = user
                            ref.accepted_dt = datetime.datetime.now()
                            ref.accepted = True
                            ref.save()
                            user.is_active = True
                            user.save()
                            mg, is_new = MyGroup.objects.get_or_create(user=user, topic=ref.topic)
                            ref.topic.group_members += 1
                            ref.topic.save()
                            return HttpResponseRedirect('/')
                        except:
                            namespace['errors'] = "Illegal Referral Key"
                else:
                    namespace['errors'] = "Inactive Account. Reply to the Confirmation Email!"

            else:
                #TODO: form is erroneous somehow, need to find out how and add to error text
                try:
                    user_exist = User.objects.get(username=form.cleaned_data['name'])
                    #if the user exists we should get to this point
                    namespace['errors'] = "Username or Password Failed"
                except:
                    namespace['errors'] = "Username or Password Failed"
        else:
            #TODO: form is empty in some way, add this message to error
            namespace['errors'] = "Seem to be Missing Something..."

    else:
        form = LoginForm()
        #if return_path != None: namespace['display'] = 'display:none;' #for ajax

    namespace['form'] = form
    output = nodelist.render(context)
    context.pop()

    return output


class LoginForm(forms.ModelForm):
    def save(self, commit=True):
        new_user = super(LoginForm, self).save(commit=False)
        return new_user

    class Meta:
        model = Login
        exclude = ('ip')
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_user_login_form")
    name = forms.CharField(label=_(u'Name'))
    password = forms.CharField(label=_(u'Pass'), widget=forms.PasswordInput(render_value=False))
