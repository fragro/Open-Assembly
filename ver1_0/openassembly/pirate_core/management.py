"""Integrates django-notification into the OpenAssembly system.
    pirate_messages.models.create_notification users signals to create 
    flexible notifications from django-notifications
"""
from django.conf import settings
from django.db.models import signals


if False:
    from pirate_consensus.models import Consensus 
    from django.contrib.auth.models import User
    from django.contrib.contenttypes.models import ContentType 
    ctype = ContentType.objects.get_for_model(User)
    cons = Consensus.objects.all()
    for c in cons:
        if c.content_type != ctype and c.content_object == None:
            c.delete()
