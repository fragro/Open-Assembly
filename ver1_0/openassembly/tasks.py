import time

from celery.task import task


"""
Scheduled phasechange task, moves consensus object from nomination
to voting phase and voting to decision phase. Events should be based
on a timedelta generated at the time of the proposal generation.
"""
@task(ignore_result=True)
def phasechange(name):
    logger = phasechange.get_logger()
    logger.info('Starting the lazy job: {0}'.format(name))
    time.sleep(5)
    logger.info('Lazy job {0} completed'.format(name))


"""
Rerenders oa_cache cache objects using a key
"""
@task(ignore_result=True)
def commit_update(name):
    logger = commit_update.get_logger()
    logger.info('Starting the lazy job: {0}'.format(name))
    time.sleep(5)
    logger.info('Lazy job {0} completed'.format(name))

"""
create a view object for this user and this page, to count the number
of views for a page, record current users viewing an object.
"""
@task(ignore_result=True)
def create_view(name):
    logger = commit_update.get_logger()
    logger.info('Starting the lazy job: {0}'.format(name))
    time.sleep(5)
    logger.info('Lazy job {0} completed'.format(name))
