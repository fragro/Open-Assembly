from celery.task import task
from pirate_forum.models import Edit
from diff_match_patch import diff_match_patch
import json
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
import datetime


@task(ignore_result=True)
def create_edit(obj_pk, user_pk, ctype_pk, text1, text2):
    selftype = ContentType.objects.get(pk=ctype_pk)
    user = User.objects.get(pk=user_pk)
    mpl = diff_match_patch()
    dd = mpl.diff_main(text1, text2)
    js = json.dumps({'diff': dd})
    new_edit = Edit(time=datetime.datetime.now(), object_pk=obj_pk, object_type=selftype, user=user, edit_diff=js)
    new_edit.save()


@task(ignore_result=False)
def patch_text(edit_pk):

    edit = Edit.objects.get(pk=edit_pk)
    diff = json.loads(edit.edit_diff)['diff']

    #get existing object text
    text = edit.content_object.description

    mpl = diff_match_patch()
    js = json.dumps(dd)['diff']

    patch = mpl.make_patch(js)
    return patch_apply(patch, text)

