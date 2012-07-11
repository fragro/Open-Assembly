from django import forms
from django import template
from pirate_core.views import namespace_get
from pirate_core.forms import FormMixin
from pirate_permissions.models import PermissionsGroup, Permission

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)


get_namespace = namespace_get("pp_permissions")


@block
def has_permissions(context, nodelist, *args, **kwargs):
    """Returns a list of users with the permission applied to the object.

    """
    context.push()
    namespace = get_namespace(context)

    name = kwargs.pop('name', None)
    obj = kwargs.pop('object', None)

    try:
        attempt = obj.is_authenticated()
    except:
        attempt = True
    if attempt:
        perm = Permission.objects.filter(name=name, object_pk=obj.pk)

        namespace['permissions'] = perm
        namespace['count'] = perm.count()

    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_permgroup_list(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    active = kwargs.pop('active', None)
    if active is not None:
        active = True if active == "True" else False
        namespace["groups"] = PermissionsGroup.objects.filter(is_active=active).all()
    else:
        namespace["groups"] = PermissionsGroup.objects.all()

    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_permgroup_list(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    active = kwargs.pop('active', None)
    if active is not None:
        active = True if active == "True" else False
        namespace["groups"] = PermissionsGroup.objects.filter(is_active=active).all()
    else:
        namespace["groups"] = PermissionsGroup.objects.all()

    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_permgroup_form(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    POST = kwargs.pop('POST', None)
    path = kwargs.pop('path', "/")

    form = GroupForm.create(POST, path)

    namespace['form'] = form
    output = nodelist.render(context)
    context.pop()

    return output


class GroupForm(forms.ModelForm, FormMixin):
    class Meta:
        model = PermissionsGroup
