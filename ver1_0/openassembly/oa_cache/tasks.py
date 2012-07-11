from datetime import datetime, timedelta
import logging
import traceback
from celery.task import task

from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from django.db.utils import DatabaseError

from tracking.utils import get_ip, u_clean, get_cleanup_timeout
from tracking.models import Visitor, UntrackedUserAgent

log = logging.getLogger('oa_cache.tasks')

"""
In this tasks files we take advantage of the tack_visitors function from the django_tracking
middleware but move it to the oa_cache.views which uses JS to override the existing request system
"""


@task(ignore_result=True)
def track_visitors(request):
    ip_address = get_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]

    # retrieve untracked user agents from cache
    ua_key = '_tracking_untracked_uas'
    untracked = cache.get(ua_key)
    if untracked is None:
        log.info('Updating untracked user agent cache')
        untracked = UntrackedUserAgent.objects.all()
        cache.set(ua_key, untracked, 3600)

    # see if the user agent is not supposed to be tracked
    for ua in untracked:
        # if the keyword is found in the user agent, stop tracking
        if unicode(user_agent, errors='ignore').find(ua.keyword) != -1:
            log.debug('Not tracking UA "%s" because of keyword: %s' % (user_agent, ua.keyword))
            return

    if hasattr(request, 'session'):
        # use the current session key if we can
        session_key = request.session.session_key
    else:
        # otherwise just fake a session key
        session_key = '%s:%s' % (ip_address, user_agent)

    # if we get here, the URL needs to be tracked
    # determine what time it is
    now = datetime.now()

    attrs = {
        'session_key': session_key,
        'ip_address': ip_address
    }

    # for some reason, Visitor.objects.get_or_create was not working here
    try:
        visitor = Visitor.objects.get(**attrs)
    except Visitor.DoesNotExist:
        # see if there's a visitor with the same IP and user agent
        # within the last 5 minutes
        cutoff = now - timedelta(minutes=5)
        visitors = Visitor.objects.filter(
            ip_address=ip_address,
            user_agent=user_agent,
            last_update__gte=cutoff
        )

        if len(visitors):
            visitor = visitors[0]
            visitor.session_key = session_key
            log.debug('Using existing visitor for IP %s / UA %s: %s' % (ip_address, user_agent, visitor.id))
        else:
            # it's probably safe to assume that the visitor is brand new
            visitor = Visitor(**attrs)
            log.debug('Created a new visitor: %s' % attrs)
    except:
        return

    # determine whether or not the user is logged in
    user = request.user
    if isinstance(user, AnonymousUser):
        user = None

    # update the tracking information
    visitor.user = user
    visitor.user_agent = user_agent

    # if the visitor record is new, or the visitor hasn't been here for
    # at least an hour, update their referrer URL
    one_hour_ago = now - timedelta(hours=1)
    if not visitor.last_update or visitor.last_update <= one_hour_ago:
        visitor.referrer = u_clean(request.META.get('HTTP_REFERER', 'unknown')[:255])

        # reset the number of pages they've been to
        visitor.page_views = 0
        visitor.session_start = now

    visitor.url = request.path
    visitor.page_views += 1
    visitor.last_update = now
    try:
        visitor.save()
    except DatabaseError:
        log.error('There was a problem saving visitor information:\n%s\n\n%s' % (traceback.format_exc(), locals()))

    timeout = get_cleanup_timeout()

    if str(timeout).isdigit():
        log.debug('Cleaning up visitors older than %s hours' % timeout)
        timeout = datetime.now() - timedelta(hours=int(timeout))
        Visitor.objects.filter(last_update__lte=timeout).delete()
