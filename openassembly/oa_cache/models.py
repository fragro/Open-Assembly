from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string
from django.shortcuts import render_to_response
from google.appengine.api import memcache
from pirate_ranking.models import get_ranked_list
from pirate_comments.models import get_comments
from pirate_deliberation.models import get_argument_list
from pirate_topics.models import get_topics
from pirate_forum.models import get_children
from django.contrib import admin
from django.core.context_processors import csrf


DIMS = {"_t": 'TYPE_KEY', "_o": "OBJ_KEY", "_s": "START_KEY",
            "_e": "END_KEY", "_d": "DIM_KEY", "_i": "S_KEY",
            '_c': "SCROLL_KEY", "_r": "SEARCH_KEY", "_l": "CTYPE_KEY"}

OPP_DIMS = {'TYPE_KEY': "_t", "OBJ_KEY": "_o", "START_KEY": "_s",
            "END_KEY": "_e", "DIM_KEY": "_d", "S_KEY": "_i",
            "SCROLL_KEY": '_c', "SEARCH_KEY": "_r", "CTYPE_KEY": "_l"}

def initiate_update(obj_pk, content_pk):
    """
    This method is designed to allow objects to access the oa_cache and update their rendered memcache file.
    If these objects
"""
    #update the listing.html
    m = ModelCache.objects.get(html="listing.html")
    #update the detail_dyn.html
    m = ModelCache.objects.get(html="detail_dyn.html")


def interpret_hash(h):
    l = h.split('/')
    retdict = {}
    rendertype = l[0]
    if rendertype[0] == '#':
        rendertype = rendertype[1:]
    key = str(rendertype)
    for dim in l[1:]:
        key += '/' + dim[0:2] + dim[2:]
        try:
            retdict[DIMS[dim[0:2]]] = dim[2:]
        except:
            pass
    return key, rendertype, retdict


def build_hash(rendertype, paramdict):
    l = '#' + rendertype
    for k, v in paramdict.items():
        l += '/' + OPP_DIMS[k] + v
    return l


class ModelCache(models.Model):
    """Stores references to cached objects with template
that will be inserted at div_id. content_type
references if this Model is a listing type for lists if
it is a ListCache, or a detailed content item/user if otherwise.
"""
    template = models.CharField(max_length=200)
    div_id = models.CharField(max_length=200)
    content_type = models.CharField(max_length=200)
    main = models.BooleanField(default=False)
    is_recursive = models.BooleanField(default=False)
    jquery_cmd = models.CharField(max_length=200, blank=True, null=True)

    def recursive_render(self, tree, context, forcerender):
        ret_html = ""
        for obj in tree:
            if isinstance(obj, list):
                context['object'] = obj[0]
                if context['object'] is not None:
                    #context['count'] = len(tree[1])
                    key = str(self.template) + '-' + str(context['object'].pk)
                    val = memcache.get(key)
                    if val is None or forcerender == True or forcerender == context['object'].pk:
                        val = render_to_string(self.template, context)
                    ret_html += '<ul id="' + self.template.replace('.html', '') + str(context['object'].pk) + '" class="' + self.template.replace('.html', '') + '">' + val
                    if len(obj) > 1:
                        ret_html += self.recursive_render(obj[1], context, forcerender) + "</ul></ul>"
                    else:
                        ret_html += '</ul>'
            else:
                context['object'] = obj
                context['count'] = 0
                if context['object'] is not None:
                    key = str(self.template) + '-' + str(context['object'].pk)
                    val = memcache.get(key)
                    if val is None or forcerender == True or forcerender == context['object'].pk:
                        val = render_to_string(self.template, context)
                    ret_html += '<ul id="' + self.template.replace('.html', '') + str(obj.pk) + '" class="' + self.template.replace('.html', '') + '">' + val + "</ul>"
        return ret_html

    def render(self, context, forcerender=False):
        #gets from cache or renders an atomic object given template
        if self.is_recursive == False:
            try:
                key = str(self.template) + '-' + str(context['object'].pk)
            except:
                key = str(self.template) + '- anon'
            obj = memcache.get(key)
            if obj is None or forcerender:
                obj = render_to_string(self.template, context)
                #obj = render_to_string(self.template, context)
                memcache.set(key, obj)
        else:
            obj = self.recursive_render([context['object']], context, forcerender)
        return obj

    def __unicode__(self):
        return '%s %s %s' % (self.template, self.div_id, self.content_type)


class ListCache(models.Model):
    model_cache = models.ForeignKey(ModelCache, null=True, blank=True)
    template = models.CharField(max_length=200)
    div_id = models.CharField(max_length=200)
    content_type = models.CharField(max_length=200)
    default = models.BooleanField(default=False)

    def get_or_create_list(self, key, paramdict, forcerender=False):
        #returns list of rendered objs
        cache = memcache.get(key)
        if cache is not None and not forcerender == True:
            cached_list = cache[0]
            tot_items = cache[1]
        elif cache is None or forcerender == True:
            if paramdict == {}:
                key, rtype, paramdict = interpret_hash(key)
            ctype_id = paramdict.get('TYPE_KEY', None)
            obj_id = paramdict.get('OBJ_KEY', None)
            start = paramdict.get('START_KEY', None)
            end = paramdict.get('END_KEY', None)
            dimension = paramdict.get('DIM_KEY', None)
            ctype_list = paramdict.get('CTYPE_KEY', None)

            if ctype_id is not None and obj_id is not None:
                content_type = ContentType.objects.get(pk=ctype_id)
                parent = content_type.get_object_for_this_type(pk=obj_id)
            else:
                parent = None

            if start is None or end is None:
                paramdict['START_KEY'] = 0
                paramdict['END_KEY'] = 20

            if dimension is None:
                dimension = 'hn'
                paramdict['DIM_KEY'] = 'hn'

            #later these functions can be rendered via some loosely coupled method
            if self.template == 'issues':
                func = get_ranked_list
                update = True
            elif self.template == 'comments':
                func = get_comments
                update = False
            elif self.template == 'yea':
                func = get_argument_list
                dimension = "yea"
                update = False
            elif self.template == 'nay':
                func = get_argument_list
                dimension = "nay"
                update = False
            elif self.template == 'children':
                func = get_children
                dimension = "children"
                update = False
            elif self.template == 'topics':
                func = get_topics
                update = True

            cached_list, tot_items = func(parent=parent, start=paramdict['START_KEY'],
                                end=paramdict['END_KEY'], dimension=dimension, ctype_list=ctype_list)
            if update:
                codes = memcache.get("rank_update_codes")
                #stores all the encoded pages for tasks/update_ranks
                newkey, rendertype, paramdict = interpret_hash(key)
                if codes is not None:
                    codes[key] = paramdict
                    memcache.replace("rank_update_codes", codes)
                else:
                    codes = {}
                    memcache.add("rank_update_codes", codes, 60)
                #save newly rendered list
            memcache.set(key, (cached_list, tot_items))
        return cached_list, tot_items

    def __unicode__(self):
        return '%s %s %s' % (self.template, self.div_id, self.content_type)


class UserSaltCache(models.Model):
    """User salt renders based on object and user,
only rendered when the corresponding model_cache is rendered"""
    model_cache = models.ForeignKey(ModelCache, blank=True, null=True)
    template = models.CharField(max_length=200)
    div_id = models.CharField(max_length=200)
    jquery_cmd = models.CharField(max_length=200)
    is_recursive = models.BooleanField(default=False)
    #if this is a toggled DIV, when re-rendered we want to toggle again
    is_toggle = models.BooleanField(default=True)
    #is this object DIV specific or required an object pk appended
    #set to TRUE if you want it OA_CACHE to append an object pk
    object_specific = models.BooleanField(default=False)
    #if this usersalt is associated with a different context, we need to redirect to that context
    redirect = models.BooleanField(default=False)
    #if this userSalt object is only used in a single page
    #we want all other views to turn off the user salt, by replacing it with an empty salt
    #thus if this model_cache is OPPOSITE, the model cache is the only one that doesn't
    #render an empty in this DIV_ID
    opposite = models.BooleanField(default=False)
    #should we cache this non-dynamic html?
    cache = models.BooleanField(default=False)
    ###does this object need to be loaded last on the page, for instance if an anchor needs to be placed first
    load_last = models.BooleanField(default=False)

    def recursive_render(self, tree, context):
        ret_html = []
        for obj in tree:
            if isinstance(obj, list):
                context['object'] = obj[0]
                #context['count'] = len(tree[1])
                ret_html.append((render_to_string(self.template, context), obj[0].pk))
                if len(obj) > 1:
                    ret_html.extend(self.recursive_render(obj[1], context))
            else:
                context['object'] = obj
                #context['count'] = 0
                ret_html.append((render_to_string(self.template, context), obj.pk))
        return ret_html

    def render(self, context, forcerender=False):
        if not self.is_recursive:
            if self.cache:
                key = str(context['object'].pk) + ' - ' + str(context['dimension']) + ' - ' + str(context['sort_type'])
                cached = memcache.get(key)
                if cached == None or forcerender:
                    r = render_to_string(self.template, context)
                    memcache.set(key, r)
                    return r
                else:
                    return cached
            return render_to_string(self.template, context)
        else:
            obj = self.recursive_render([context['object']], context)
            return obj

    def __unicode__(self):
        return '%s %s' % (self.template, self.div_id)


class SideEffectCache(models.Model):
    """User salt renders based on object and user,
only rendered when the corresponding model_cache is rendered"""
    user_salt_cache = models.ForeignKey(UserSaltCache)
    template = models.CharField(max_length=200)
    div_id = models.CharField(max_length=200)
    jquery_cmd = models.CharField(max_length=200)
    #is this object DIV specific or required an object pk appended
    #set to TRUE if you want it OA_CACHE to append an object pk
    object_specific = models.BooleanField(default=False)

    def render(self, context):
        return render_to_string(self.template, context)

    def __unicode__(self):
        return 'USC : %s -- (%s %s)' % (self.user_salt_cache, self.template, self.div_id)


admin.site.register(UserSaltCache)
admin.site.register(ListCache)
admin.site.register(ModelCache)
admin.site.register(SideEffectCache)
