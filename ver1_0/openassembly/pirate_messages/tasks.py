from celery.task import task


@task(ignore_results=True)
def set_to_read(notes):
    for i in notes:
        i.is_read = True
        i.save()
