from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
import datetime
import django.dispatch
from django.contrib import admin
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from pirate_profile.models import Profile
from pirate_signals.models import notification_send
from django import forms
from markitup.widgets import MarkItUpWidget
from notification import models as notification
import settings
from pirate_comments.models import Comment


class Message(models.Model):
    sender = models.ForeignKey(User, null=True, related_name="message_sender")
    receiver = models.ForeignKey(User, related_name="message_receiver")
    parent_pk = models.IntegerField(_('Parent Message PK'), blank=True, null=True)
    description = models.TextField(max_length=1200)
    created_dt = models.DateTimeField()
    read = models.BooleanField()

    def __unicode__(self):
        if len(self.description) > 100:
            return str(self.description[0:100] + '[...]')
        else:
            return str(self.description)


class Notification(models.Model):
    receiver = models.ForeignKey(User, related_name="notification_receiver")
    sender = models.ForeignKey(User, related_name="notification_sender")
    text = models.TextField(max_length=1200)
    link = models.CharField(max_length=250)
    content_type = models.ForeignKey(ContentType,
                                      verbose_name=_('content type'),
                                      related_name="content_type_set_for_%(class)s")
    object_pk = models.CharField(_('object ID'), max_length=100)
    content_object = generic.GenericForeignKey(ct_field="content_type", fk_field="object_pk")
    is_read = models.BooleanField()
    submit_date = models.DateTimeField("date_sent")

    def __unicode__(self):
        return str(self.content_type) + ':' + str(self.object_pk)


class MessageForm(forms.ModelForm):

    def save(self, commit=True):
        newo = super(MessageForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = Message
        exclude = ('receiver', 'sender', 'created_dt', 'read', 'parent_pk')

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_message_form")
    description = forms.CharField(widget=MarkItUpWidget(), label="Description")


def create_notification(obj, reply_to, **kwargs):
    #obj specifies the obj being replied to, new_obj specifies the new object
    try:
        profile = Profile.objects.get(user=reply_to.user)
        send_email = profile.receive_emails
    except:
        send_email = True
    content_type = ContentType.objects.get_for_model(obj)
    rep_type = ContentType.objects.get_for_model(reply_to)
    link = kwargs.get('link', None)
    text = kwargs.get('text', None)
    user_type = ContentType.objects.get_for_model(User)
    if content_type is not user_type and rep_type is not user_type:
        if obj.user != reply_to.user:
            path = obj.get_absolute_url()
            #if this notification is a comment_reply
            if str(content_type) == 'comment':
                if str(rep_type) == 'comment':
                    summ = str(reply_to.text)
                else:
                    summ = str(reply_to.summary)
                if send_email:
                        notification.send([reply_to.user], "comment_reply", {"from_user": obj.user, "user_url": settings.DOMAIN + obj.user.get_absolute_url(),
                        "notice_message": "New comment received for your " + str(rep_type) + " '" + summ + "':",
                        "reply": str(obj.text), "path": settings.DOMAIN + path})
                if len(obj.text) > 30:
                    tt = str(obj.text)[0:30] + "..."
                else:
                    tt = str(obj.text)
                text = str(obj.user.username) + " replied to your " + str(rep_type) + ": " + tt
                link = obj.get_absolute_url()

            #if notification is an action_reply
            elif str(content_type) == 'action taken':
                if send_email and not settings.DEBUG:
                        notification.send([reply_to.user], "action_reply", {"from_user": obj.user, "user_url": settings.DOMAIN + obj.user.get_absolute_url(),
                        "notice_message": str(obj.user.username) + " acted on your " + str(rep_type) + " : " + str(reply_to.summary),
                        "path": settings.DOMAIN + path})

                text = str(obj.user.username) + " acted on your " + str(rep_type)
                link = reply_to.get_absolute_url()

            elif str(content_type) == 'argument':
                if send_email:
                        notification.send([reply_to.user], "argument_reply", {"from_user": obj.user, "user_url": settings.DOMAIN + obj.user.get_absolute_url(),
                        "notice_message": "New argument received for your " + str(rep_type) + " " + str(reply_to.summary),
                        "path": settings.DOMAIN + path})
                text = str(obj.user.username) + " created an argument for your " + str(rep_type)
                link = reply_to.get_absolute_url()

            #if notification is badge_received

        #elif str(content_type) == 'badge':
        #    content_type = ContentType.objects.get_for_model(User)
        #    path = "/index.html#user/t-" + str(content_type.pk) + "/o-" + str(obj.user.pk)
        #    if send_email:
        #            notification.send([reply_to.user], "badge_received", {"from_user": obj.user,
        #        "notice_message": str(obj.user.username) + ", you've received a " + str(rep_type) + " '" + str(reply_to.dimension.name) + "':",
        #        "path": settings.DOMAIN_NAME + path})
        #    text = "you received a " + str(reply_to.dimension.name) + " badge"
        #    link = reply_to.get_absolute_url()

            #if notification is a child_reply

            #if notification is a message_received

            #if notification is support_Created

            #if notification is an argument_reply

    if link is not None and text is not None:
        if user_type != rep_type:
            notif = Notification(receiver=reply_to.user, sender=obj.user, text=text, link=link, content_type=rep_type, object_pk=reply_to.pk, is_read=False, submit_date=datetime.datetime.now())
        else:
            notif = Notification(receiver=reply_to, sender=obj, text=text, link=link, content_type=rep_type, object_pk=reply_to.pk, is_read=False, submit_date=datetime.datetime.now())
        notif.save()

notification_send.connect(create_notification)
admin.site.register(Notification)
