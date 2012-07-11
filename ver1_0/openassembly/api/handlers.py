from piston.handler import BaseHandler
from pirate_forum.models import ForumDimension
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from pirate_profile.models import Profile
from pirate_consensus.models import UpDownVote, RatingVote
from pirate_core.templatetags.tag_helpers import get_link_tag_list
from pirate_sources.models import URLSource
from django.db.models import get_model
from pirate_consensus.models import Consensus
from oa_platform.models import Platform, PlatformDimension
from collections import defaultdict
from django.forms.models import model_to_dict


class PlatformDimensionHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, obj_id=None):
        """
        Returns a list of platforms specific to this content_type and Group ID
        """
        dims = PlatformDimension.objects.filter(complete=False)
        if obj_id is not None:
            dims = dims.filter(object_pk=obj_id)
        content = []
        for i in dims:
            content.append({'app_label': i.content_type.app_label, 'model': i.content_type.model, 'dimension': i})
        return content


class PlatformHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, app=None, model=None, obj_id=None):
        """
        Returns a list of platforms specific to this content_type and Group ID
        """
        if app is not None and model is not None and obj_id is not None:
            try:
                base = ContentType.objects.get(app_label=app, model=model)
                platdim = PlatformDimension.objects.get(content_type=base, object_pk=obj_id, complete=False)
                platforms = Platform.objects.filter(dimension=platdim)
                return {'platforms': platforms}
            except:
                return {'error': True, 'type': 'Platforms Not Found',
                        'code': 404, 'app': app, 'model': model}

        else:
            content = {'error': True, 'type': 'Must Specify App/Model and ID of Group',
                            'id': int(obj_id), 'code': 404}

            return content


class GroupContentHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, parent=None):
        """
        Returns a single post if `blogpost_id` is given,
        otherwise a subset.

        """
        if parent is not None:
            content = {}
            for fd in ForumDimension.objects.filter(is_content=True):
                content[fd.app_label +
                    '_' + fd.model_class_name.lower()] = (fd.get_model().objects.filter(parent_pk=parent))
            return content
        else:
            return {'error': True, 'type': 'Must Supply Parent Argument'}


class ContentHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, app=None, model=None, obj_id=None):
        """
        Returns a single post if `blogpost_id` is given,
        otherwise a subset.

        """
        if app is not None and model is not None:
            try:
                base = ContentType.objects.get(app_label=app, model=model)
            except:
                return {'error': True, 'type': 'Content Not Found',
                        'code': 404, 'app': app, 'model': model}
            if obj_id is not None:
                try:
                    con = Consensus.objects.get(object_pk=obj_id)
                    obj = base.get_object_for_this_type(pk=obj_id)
                    #get tags from convienent tag_helper function
                    tags = get_link_tag_list(None, con)
                    return {'id': obj.id,
                        'user_id': obj.user.id,
                        'object': base.get_object_for_this_type(pk=obj_id),
                        'tags': [{'name': i[0], 'count': i[3]} for i in tags],
                        'parent': obj.parent.id,
                        'sources': URLSource.objects.filter(object_pk=obj.pk,
                                                             is_video=False)
                        }
                except:
                    return {'error': True, 'type': 'Content Not Found',
                            'id': int(obj_id), 'code': 404}
            else:
                return base.model_class().objects.all()
        else:
            content = {}
            for fd in ForumDimension.objects.filter(is_content=True):
                content[fd.app_label +
                    '_' + fd.model_class_name.lower()] = (fd.get_model().objects.all())
            return content


class UserHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, obj_id=None):
        """
        Returns a single post if `blogpost_id` is given,
        otherwise a subset.

        """
        if obj_id is not None:
            try:
                u = User.objects.get(pk=obj_id)
                u = {'id': u.id, 'is_active': u.is_active}
                try:
                    p = Profile.objects.get(user=u)
                except:
                    p = None
                plats = Platform.objects.filter(user=u)
                pdict = {}
                for p in plats:
                    pdict[str(p.content_type)] = p.planks
                return {'id': u.id, 'user': u, 'profile': p,
                'platforms': pdict}
            except:
                return {'id': int(obj_id), 'error': True,
                        'type': 'User Not Found', 'code': 404}
        else:
            users = User.objects.all()
            users = [{'id': u.id, 'is_active': u.is_active} for u in users]
            return users


class VoteHandler(BaseHandler):
    allowed_methods = ('GET',)
    exclude = ('user')

    def read(self, request, model=None, obj_id=None):
        """
        Returns a single post if `blogpost_id` is given,
        otherwise a subset.
        """
        if model is not None:
            if model == 'objective':
                model = 'ratingvote'
            elif model == 'subjective':
                model = 'updownvote'
            m = get_model('pirate_consensus', model)
            if obj_id is not None:
                obj = m.objects.get(pk=obj_id)
                if obj is not None:
                    try:
                        user_id = obj.user.id
                    except:
                        return {'error': True, 'type': 'Vote User Not Found',
                        'code': 404}
                    obj = model_to_dict(obj, fields=[], exclude=[])
                    del obj['user']
                    return {'id': obj['id'], 'content_id': obj['object_pk'],
                                'user_id': user_id, 'vote': obj}
                else:
                    return {'error': True, 'type': 'Vote Not Found',
                        'code': 404}

            else:
                return m.objects.all()
        else:
            return {'objective': RatingVote.objects.all(),
                    'subjective': UpDownVote.objects.all()}


class PKHandler(BaseHandler):
    allowed_methods = ('GET',)

    def read(self, request, pk_type=None):
        """
        Returns a single post if `blogpost_id` is given,
        otherwise a subset.
        """
        if pk_type == 'content':
            ret = []
            #for different forms using the same object
            complete = []
            for fd in ForumDimension.objects.all():
                pk_id = [str(fd.app_label),
                        str.lower(str(fd.model_class_name))]
                if pk_id not in complete:
                    dim = fd.get_model().objects.values('pk')
                    ret.append({'params': [str(fd.app_label),
                                        str.lower(str(fd.model_class_name))],
                            'ids': dim})
                    complete.append(pk_id)
            return ret
        elif pk_type == 'user':
            return [u.pk for u in User.objects.all()]
        elif pk_type == 'vote':
            return [{'params': ['objective'],
                     'ids': RatingVote.objects.values('pk')},
                    {'params': ['subjective'],
                     'ids': UpDownVote.objects.values('pk')}]
        else:
            return {'error': True, 'type': 'PK Type Unknown',
                    'code': 404}
