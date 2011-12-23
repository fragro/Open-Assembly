from django import template
from django import forms
from django.http import HttpResponseRedirect
import datetime
from django.contrib.contenttypes.models import ContentType

from oa_verification.models import EmailVerification
import datetime, random, sha
from django.core.mail import send_mail

from oa_verification.models import ActionTaken

from pirate_topics.models import MyGroup

from settings import DOMAIN_NAME, EMAIL_HOST_USER

from pirate_permissions.models import PermissionsGroup, Permission

from pirate_core import HttpRedirectException, namespace_get, FormMixin

from pirate_signals.models import aso_rep_event, notification_send, relationship_event


from django.contrib.auth.models import User
from pirate_sources.models import IMGSource
from oa_verification.models import arpv, PhotoVerificationTask, PhotoUserVerifications, Referral
from oa_verification.forms import arpvForm, ReferralForm
from pirate_core.widgets import HorizRadioRenderer
from collections import defaultdict

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('oa_ver')


class ActionTakenForm(forms.ModelForm):

    def save(self, commit=True):
        new_source = super(ActionTakenForm, self).save(commit=commit)
        return new_source

    class Meta:
        model = ActionTaken
        exclude = ('user', 'content_object','object_pk','content_type')

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_actiontaken_form")


@block
def oa_actiontaken_form(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    POST = kwargs.get('POST', None)
    obj = kwargs.get('object', None)
    user = kwargs.get('user', None)

    content_type = ContentType.objects.get_for_model(obj)
    path = 'detail.html' + "?_t=" + str(content_type.pk) + "&_o=" + str(obj.pk)

    if POST:
        form = ActionTakenForm(POST)
        if form.is_valid():
            newobj = form.save(commit=False)
            newobj.user = user
            newobj.content_type = content_type
            newobj.object_pk = obj.pk
            newobj.save()
            notification_send.send(sender=newobj, obj=newobj, reply_to=obj)
            relationship_event.send(sender=newobj, obj=newobj, parent=obj)

            #raise HttpRedirectException(HttpResponseRedirect(path))
        else:
            namespace['errors'] = form.errors

    form = ActionTakenForm()

    namespace['form'] = form
    output = nodelist.render(context)
    context.pop()

    return output


@block
def oa_get_actiontaken(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    obj = kwargs.get('object', None)

    try:
        obj = ActionTaken.objects.get(object_pk=obj.pk)
        action_taken = True
        namespace['url'] = obj.url
        try:
            namespace['verb'] = obj.verb
        except:
            namespace['verb'] = "Action Taken"
    except:
        action_taken = False

    namespace['has_action_taken'] = action_taken
    output = nodelist.render(context)
    context.pop()

    return output


@block
def oa_get_verifications(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    try:
        obj = PhotoUserVerifications.objects.get(user=user)
        namespace['count'] = obj.verifications
    except:
        namespace['count'] = 0

    try:
        ref = Referral.objects.get(accepted_user=user)
        namespace['count'] += 1
    except:
        pass

    output = nodelist.render(context)
    context.pop()

    return output


@block
def oa_get_referral(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    key = kwargs.get('key', None)

    try:
        ref = Referral.objects.get(key=key)
    except:
        ref = None

    namespace['referral'] = ref

    output = nodelist.render(context)
    context.pop()

    return output


@block
def oa_activate_referral(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    key = kwargs.get('key', None)
    user = kwargs.get('user', None)

    try:
        ref = Referral.objects.get(key=key)

        if ref.email == user.email:
            ref.referred_user = user
            ref.accepted_dt = datetime.datetime.now()
            ref.accepted = True
            ref.save()
            if ref.topic is not None:
                myg = MyGroup.objects.get_or_create(topic=ref.topic, user=user)
        else:
            namespace['errors'] = 'Email not associated with this account. Log into account associated with ' + str(ref.email) + ' and try again.'
    except:
        ref = None

    namespace['referral'] = ref

    output = nodelist.render(context)
    context.pop()

    return output


class FacilitatorsForm(forms.Form):

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="oa_facilitators_form")
    username = forms.CharField(max_length=300)


@block
def oa_facilitators_form(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    new_topic = kwargs.get('object', None)
    POST = kwargs.get('POST', None)

    if POST is not None and POST.get("form_id") == "oa_facilitators_form":
        form = FacilitatorsForm(POST)
        if form.is_valid():
            try:
                user = User.objects.get(username=form.cleaned_data['username'])
                ctype = ContentType.objects.get_for_model(new_topic)
                #create Facilitator permissions for group creator
                perm_group, is_new = PermissionsGroup.objects.get_or_create(name="Facilitator", description="Permission group for Facilitation of Online Working Groups")
                perm, newperm = Permission.objects.get_or_create(user=user, name='facilitator-permission', content_type=ctype,
                            object_pk=new_topic.pk, permissions_group=perm_group, component_membership_required=True)
                mg, newgr = MyGroup.objects.get_or_create(topic=new_topic, user=user)
                namespace['done'] = form.cleaned_data['username'] + ' added'
            except:
                namespace['error'] = 'Username not Found'
        else:
            namespace['errors'] = form.errors
    else:
        form = FacilitatorsForm()

    namespace['form'] = form
    output = nodelist.render(context)
    context.pop()

    return output


@block
def oa_referral_form(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    POST = kwargs.get('POST', None)
    obj = kwargs.get('object', None)
    namespace['errors'] = []
    sent = 0

    if POST:
        form = ReferralForm(POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            email_list = email.replace(' ', '').split(',')
            for email in email_list:
                try:
                    ref = Referral.objects.get(email=email, topic=obj)
                    namespace['errors'].append('Referral Key Already Used for this group and email: ' + str(email))
                except:
                    #create referral
                    salt = sha.new(str(random.random())).hexdigest()[:5]
                    activation_key = sha.new(salt + user.username).hexdigest()
                    ref = Referral(topic=obj, user=user, created_dt=datetime.datetime.now(),
                                    key=activation_key, email=email, accepted=False)
                    ref.save()
                    #send referral email
                    email_subject = 'OpenAssembly Referral to ' + str(obj.shortname)
                    if obj:
                        email_subject += " to Group " + str(obj)
                    email_body = "You've been referred to OpenAssembly by %s. \n\nTo join as a verified user:\n\n%sregister.html?_d=%s" % (
                        user.username, DOMAIN_NAME,
                        ref.key)
                    send_mail(email_subject,
                              email_body,
                              'fragro@gmail.com',
                              [user.email])
                    sent += 1
            namespace['errors'].append("Mail sent to " + str(sent) + " recipients")

        else:
            namespace['errors'].append(form.errors)
    else:
        form = ReferralForm()
    namespace['form'] = form

    output = nodelist.render(context)
    context.pop()

    return output


@block
def oa_ver_form(context, nodelist, *args, **kwargs):
    '''form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_arpv_form")
    This block tag creates instances of anonymous photo verification tags, and makes sure
    that the users exist, they are not the same, and
    Usage is as follows:

    {% pp_arpv_form POST=request.POST user=request.user%}
       Do stuff with {{ pp_arpv.form }}.
    {% endpp_arpv_form%}
    '''
    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    POST = kwargs.get('POST', None)
    FILE = kwargs.get('FILE', None)

    ctype = ContentType.objects.get_for_model(user)
    if POST:
        form = arpvForm(POST, FILE)
        if form.is_valid():
            try:
                userobj1 = User.objects.get(username=form.cleaned_data.get('user1'))
                test1 = True
            except:
                test1 = False
            try:
                userobj2 = User.objects.get(username=form.cleaned_data.get('user2'))
                test2 = True
            except:
                test2 = False
            if userobj1 == userobj2:
                namespace['errors'] = 'The users are the same'
            elif not test1:
                namespace['errors'] = 'User1 does not Exist'
            elif not test2:
                namespace['errors'] = 'User2 does not Exist'
            elif not test1 and not test2:
                namespace['errors'] = 'Neither User Exists'
            else:
                photo = form.cleaned_data['photo']
                temp = arpv(user1=userobj1, user2=userobj2, photo=photo)
                temp.submit_user = user
                #if the submit user is one of the photo users, this should be normal
                if temp.submit_user == userobj1:
                    temp.user1Confirm = True
                elif temp.submit_user == userobj2:
                    temp.user2Confirm = True
                temp.created_dt = datetime.datetime.now()
                temp.save()
                #now that we have saved the arpv, send out notifications for confirmation
                if not temp.user1Confirm:
                    link = temp.get_absolute_url()
                    text = 'Click Here to Confirm a Photo of You from ' + str(user.username)
                    notification_send.send(sender=temp, obj=user, reply_to=userobj1, link=link, text=text)
                if not temp.user2Confirm:
                    link = temp.get_absolute_url()
                    text = 'Click Here to Confirm a Photo of You from ' + str(user.username)
                    notification_send.send(sender=temp, obj=user, reply_to=userobj2, link=link, text=text)
                #raise HttpRedirectException(HttpResponseRedirect(returnurl))
                form = arpvForm()
                if user is not None:
                    arpvs = arpv.objects.filter(submit_user=user)
                namespace['photo_ids'] = [i.photo.pk for i in arpvs]
                form.fields['photo'].queryset = IMGSource.objects.filter(object_pk=user.pk, content_type=ctype)
                namespace['arpvs'] = arpvs
            namespace['form'] = form
        else:
            namespace['errors'] = 'Invalid Entry. Make Sure You Have Selected a Photo and 2 Users'
            form = arpvForm()
            form.fields['photo'].queryset = IMGSource.objects.filter(object_pk=user.pk, content_type=ctype)
    else:
        #if user is not None:
        form = arpvForm()
        form.fields['photo'].queryset = IMGSource.objects.filter(object_pk=user.pk, content_type=ctype)
    namespace['form'] = form
    output = nodelist.render(context)
    context.pop()

    return output


CHOICES = (
    (1, 'YES'),
    (0, 'NO')
)


class ARPVConfirmForm(forms.Form):
    choose = forms.ChoiceField(choices=CHOICES,
            widget=forms.RadioSelect())


@block
def oa_ver_confirm_form(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    val = kwargs.get('arpv', None)
    POST = kwargs.get('POST', None)

    if POST is not None and POST.get("form_id") == "oa_arpv_task_form":
        form = ARPVConfirmForm(POST)
        if form.is_valid():
            #set the appropriate user as confirmed
            choice = form.cleaned_data['choose']
            if choice == '1':
                if user == val.user1:
                    val.user1Confirm = True
                elif user == val.user2:
                    val.user2Confirm = True
                val.save()
                if val.user1Confirm and val.user2Confirm:
                    create_task(val, val.user1)
                    create_task(val, val.user2)
                raise HttpRedirectException(HttpResponseRedirect('arpv_thanks.html'))
            elif choice == '0':
                raise HttpRedirectException(HttpResponseRedirect('arpv_flag.html'))
        else:
            namespace['errors'] = form.errors
    else:
        form = ARPVConfirmForm()

    namespace['form'] = form
    output = nodelist.render(context)
    context.pop()

    return output


def create_task(val, user):
    #creates photo verification tasks for each pair of photos
    old_arpvs1 = arpv.objects.filter(user1=user).exclude(pk=val.pk)
    old_arpvs2 = arpv.objects.filter(user2=user).exclude(pk=val.pk)
    create = datetime.datetime.now()
    for i in list(old_arpvs1) + list(old_arpvs2):
        try:
            #if the mirror of this task has already been created
            old_task = PhotoVerificationTask.objects.get(pv1=val, pv2=i,
                        user1=val.user1, user2=val.user2,
                        user3=i.user1, user4=i.user2)
        except:
            #the mirror doesn't exist, get or create task
            new_task, is_new = PhotoVerificationTask.objects.get_or_create(pv1=i, pv2=val,
                            user1=i.user1, user2=i.user2,
                            user3=val.user1, user4=val.user2,
                            created_dt=create)
            if is_new:
                new_task.save()


@block
def oa_ver_task(context, nodelist, *args, **kwargs):
    '''
        This form checks to see if the user has permission
        to perform this task, then if so provide
        task form.

        If user responds, we save the task as verified and complete
        and normalize out the verification to the users and photos
        themselves.
    '''
    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    POST = kwargs.get('POST', None)
    task = kwargs.get('task', None)

    if user.is_authenticated() and user.is_staff:
        #for now only expose task to staff
        if POST and task is not None:
            form = ARPVConfirmForm(POST)
            if form.is_valid():
                choice = form.cleaned_data['choose']
                if choice == '1':
                    task.complete = True
                    task.verification = True
                    task.verified_dt = datetime.datetime.now()
                    task.verified_by = user
                    #normalize verifications to each photo
                    #ERR: for some reason we cannot pickle get_user?
                    #deferred.defer(normalize, task, _countdown=60)
                    normalize(task)
                elif choice == '0':
                    task.complete = True
                    task.verification = False
                    task.verified_dt = datetime.datetime.now()
                    task.verified_by = user
                task.save()
                #form = ARPVConfirmForm()
                namespace['form_complete'] = 'Verification Complete. Thankyou.'
                #raise HttpRedirectException(HttpResponseRedirect('arpv_task.html'))
            else:
                namespace['errors'] = form.errors

        else:
            form = ARPVConfirmForm()
            namespace['form'] = form

    output = nodelist.render(context)
    context.pop()
    return output


def normalize(task):
    #normalizes our verification as a background task
    task.pv1.verifications += 1
    task.pv2.verifications += 1
    #normalize to user
    d = defaultdict(int)
    for u in (task.user1, task.user2, task.user3, task.user4):
        d[str(u.username)] += 1
    for k, v in d.items():
        if v == 2:
            u = User.objects.get(username=k)
            val, is_new = PhotoUserVerifications.objects.get_or_create(user=u)
            val.verifications += 1
            val.save()
    task.pv1.save()
    task.pv2.save()


@block
def oa_get_arpvs(context, nodelist, *args, **kwargs):
    '''form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_arpv_form")
    This block tag creates instances of anonymous photo verification tags, and makes sure
    that the users exist, they are not the same, and
    Usage is as follows:

    {% oa_get_arpvs  user=request.user%}
       Do stuff with {{ oa_arpv.arpvs }}.
    {% endoa_get_arpvs %}
    '''
    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    arpv_img = kwargs.get('img', None)

    if user is not None:
        arpvs = arpv.objects.filter(submit_user=user)
    if arpv_img is not None:
        arpvs = arpv.objects.filter(photo=arpv_img)
    used_photos = [i.photo.pk for i in arpvs]

    namespace['arpvs'] = arpvs
    namespace['count'] = arpvs.count()
    namespace['photo_ids'] = used_photos
    output = nodelist.render(context)
    context.pop()
    return output


@block
def oa_get_users(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    users = User.objects.all()
    namespace['users'] = users

    output = nodelist.render(context)
    context.pop()
    return output


@block
def oa_get_task_count(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    tasks = PhotoVerificationTask.objects.filter(complete=False)
    count = tasks.count()
    #if this user is in either photo, he can't do the task

    namespace['count'] = count

    output = nodelist.render(context)
    context.pop()
    return output


@block
def oa_get_task(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)

    tasks = PhotoVerificationTask.objects.filter(complete=False)
    count = tasks.count()
    #if this user is in either photo, he can't do the task

    tasks = tasks.order_by('-created_dt')
    try:
        for itr in range(count):
            task = tasks[itr]
            #check if user is eligible for task
            if is_eligible(task, user):
                namespace['task'] = task
                break
    except:
        namespace['errors'] = 'Sorry, Tasks unavailable: ' + str(tasks.count()) + ' tasks.'

    output = nodelist.render(context)
    context.pop()
    return output


def is_eligible(t, u):
    if u != t.user1 and u != t.user2 and u != t.user3 and u != t.user4:
        return True
    else:
        return False
