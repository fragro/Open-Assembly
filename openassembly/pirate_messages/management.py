"""Integrates django-notification into the OpenAssembly system.
    pirate_messages.models.create_notification users signals to create 
    flexible notifications from django-notifications
"""
from django.db.models import signals
from django.conf import settings
from django.utils.translation import ugettext_noop as _

if "notification" in settings.INSTALLED_APPS:
    from notification import models as notification

    def create_notice_types(app, created_models, verbosity, **kwargs):
        notification.create_notice_type("comment_reply", _("Comment Received"), _("someone has commented on your content"))
        notification.create_notice_type("argument_reply", _("Argument Received"), _("someone has submitted an argument to your content"))
        notification.create_notice_type("child_reply", _("Reply Received"), _("someone has submitted a reply to your content"))
        notification.create_notice_type("action_reply", _("Action Taken"), _("someone has taken action on your idea"))
        notification.create_notice_type("support_created", _("Support Added"), _("someone now supports you"))
        notification.create_notice_type("badge_received", _("Badge Recieved"), _("you received a new badge"))
        notification.create_notice_type("message_received", _("Message Recieved"), _("someone sent you a message"))
    

    signals.post_syncdb.connect(create_notice_types, sender=notification)
else:
    print "Skipping creation of NoticeTypes as notification app not found"

