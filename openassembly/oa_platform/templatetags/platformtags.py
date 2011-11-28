from django import template
from oa_platform.models import Platform, PlatformDimension
from pirate_core import namespace_get
from django.contrib.contenttypes.models import ContentType
from pirate_consensus.models import Consensus
from django import forms
from pirate_core.fields import JqSplitDateTimeField
from pirate_core.widgets import JqSplitDateTimeWidget
from customtags.decorators import block_decorator
from pirate_forum.models import ForumDimension


register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('oa_platform')


@block
def pp_is_in_platform(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    object_pk = kwargs.get('object_pk', None)
    platform = kwargs.get('platform', None)

    namespace['is_in'] = object_pk in platform.planks

    output = nodelist.render(context)
    context.pop()

    return output


@block
def oa_get_platform(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    platdim = kwargs.get('platformdimension', None)
    get_cons = kwargs.get('get_consensus', None)

    if user is not None:
        #get platform for this contenttype and user
        if platdim is not None:
            pl, is_new = Platform.objects.get_or_create(user=user,
                                content_type=platdim.content_type, dimension=platdim)

            if get_cons is None:
                namespace['planks'] = [platdim.content_type.get_object_for_this_type(pk=obj_id) for obj_id in pl.planks]
            else:
                namespace['planks'] = [Consensus.objects.get(object_pk=obj_id) for obj_id in pl.planks]
            namespace['completion'] = int(float(len(namespace['planks']) / float(platdim.num_planks)) * 100)
            namespace['platform'] = pl

    output = nodelist.render(context)
    context.pop()

    return output


@block
def oa_get_platform_dimensions(context, nodelist, *args, **kwargs):
    context.push()
    namespace = get_namespace(context)

    obj = kwargs.get('object', None)
    complete = kwargs.get('complete', None)

    if obj is not None:
        pl = PlatformDimension.objects.filter(object_pk=obj.pk)
        if complete:
            pl = pl.filter(complete=bool(complete))
    else:
        pl = []

    namespace['platform_dimensions'] = pl
    if pl != []:
        namespace['count'] = pl.count()
    else:
        namespace['count'] = 0

    output = nodelist.render(context)
    context.pop()

    return output


@block
def oa_platform_form(context, nodelist, *args, **kwargs):

    """
    Allows facilitators of a group to initiate a platform for that group.
    """

    context.push()
    namespace = get_namespace(context)

    POST = kwargs.get('POST', None)
    parent = kwargs.get('object', None)
    edit = kwargs.get('edit_platform', None)
    user = kwargs.get('user', None)
    dimension = kwargs.get('dimension', None)

    if POST and POST.get("form_id") == "oa_platform_form" and user is not None and dimension is not None:
        form = PlatformDimensionForm(POST) if edit is None else PlatformDimensionForm(POST, instance=edit)
        if form.is_valid():
            new_platform = form.save(commit=False)
            fd = ForumDimension.objects.get(key=dimension)
            new_platform.content_type_obj = ContentType.objects.get_for_model(parent)
            new_platform.object_pk = parent.pk
            new_platform.content_type = ContentType.objects.get_for_model(fd.get_model())
            new_platform.initiator = user
            new_platform.save()
            #raise HttpRedirectException(HttpResponseRedirect("/topics.html"))
            namespace['errors'] = 'complete'
            namespace['object_pk'] = new_platform.pk
            ctype = ContentType.objects.get_for_model(new_platform)
            namespace['content_type'] = ctype.pk
            #create Facilitator permissions for group creator
        else:
            namespace['errors'] = form.errors
    else:
        form = PlatformDimensionForm() if edit is None else PlatformDimensionForm(instance=edit)

    namespace['form'] = form
    output = nodelist.render(context)
    context.pop()

    return output


class PlatformDimensionForm(forms.ModelForm):

    def save(self, commit=True):
        newo = super(PlatformDimensionForm, self).save(commit=commit)
        return newo

    class Meta:
        model = PlatformDimension
        exclude = ('content_type_obj', 'object_pk', 'content_type')

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="oa_platform_form")
    deadline_dt = JqSplitDateTimeField(widget=JqSplitDateTimeWidget(attrs={'date_class': 'datepicker', 'time_class': 'timepicker'}))
    vote_deadline_dt = JqSplitDateTimeField(widget=JqSplitDateTimeWidget(attrs={'date_class': 'datepicker', 'time_class': 'timepicker'}))
