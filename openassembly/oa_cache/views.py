from django.core.cache import cache as memcache
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
import simplejson
from django.template.loader import render_to_string
from django.contrib.contenttypes.models import ContentType
from oa_cache.models import ListCache, ModelCache, UserSaltCache, interpret_hash, SideEffectCache
from pirate_forum.models import create_view, get_rangelist
from django.template import RequestContext
from pirate_topics.models import Topic
from django.contrib.auth.models import User
from settings import DOMAIN


def get_object_or_none(ctype_id, obj_id):
    """
Returns object with ID and ContentType ID
"""
    if ctype_id is not None and obj_id is not None and ctype_id != '' and obj_id != '':
        content_type = ContentType.objects.get(pk=ctype_id)
        try:
            obj = content_type.get_object_for_this_type(pk=obj_id)
        except:
            obj = None
    else:
        obj = None
    return obj


def side_effect(request):
    """
Initiates AJAX side effects, for instance if a user
creates a new object, it renders that new object into the
page and deferrs a pre-rendering task for that list
and object.

This allows the user to see the immediate effect of the
action while ensuring low-latency. See the oa_cache.models
for more information on SideEffectCache
"""
    if request.method == "GET":
        rendered_list = []
        data = {}
        usc_pk = request.GET.get('usc_pk')
        se = request.GET.get('side_effect')
        parent_pk = request.GET.get('obj_pk')
        try:
            jsonval = simplejson.loads(se)
        except:
            jsonval = None
        #if there is side effect information
        if jsonval != None:
            obj_id, ctype_id = simplejson.loads(se)
            obj = get_object_or_none(ctype_id, obj_id)
            usc = UserSaltCache.objects.get(pk=usc_pk)
            #First, check to see if we need to switch context
            #EDGE-CASE: if user is viewing comments and submits argument
            if usc.redirect:
                path = obj.get_absolute_url()
                rendered_list.append({'scroll_to': False, 'div': '', 'type': 'redirect', 'html': path})
            #Now render side effects if they haven't been rendered by the change in context
            else:
                sideeffects = SideEffectCache.objects.filter(user_salt_cache=usc.pk)
                for s in sideeffects:
                    if s.object_specific:
                        div = s.div_id + str(parent_pk)
                    else:
                        div = s.div_id
                    #if usc.model_cache is not None:
                    #    if obj == None:
                    #        user = obj
                    #    else:
                    #        user = obj.user
                        #deferred.defer(usc.model_cache.render, {'object': obj, 'user': user}, True)

                    rendered_list.append({'scroll_to': s.scroll_to, 'div': div, 'type': s.jquery_cmd, 'html':
                                        s.render(RequestContext(request, {'salted': True, 'object': obj, 'user': request.user}))})
            data['output'] = rendered_list
            data['FAIL'] = False
            #deferred.defer(get_cache_or_render, request.user, key, False, True, None)

        else:
            #if the side effect is null
            data['FAIL'] = True
            data['message'] = "Malformed JSON from UserSaltCache Form"
        if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            return HttpResponse(simplejson.dumps(data),
                                mimetype='application/json')


def post_cache(user, key, div, request):
    """
Posts an AJAX response to the cache using the UserSaltCache object
as a reference for the template, div, and other necessary inforamtion.

"""
    if key is not None:
        key, rendertype, paramdict = interpret_hash(key)
        rendered_list = []
        u = UserSaltCache.objects.filter(template=div + '.html')

        csrf_val = request.COOKIES.get('csrftoken', None)
        csrf_t = "<div style='display:none'><input type='hidden' value='" + str(csrf_val) + "' name='csrfmiddlewaretoken'></div>"
        for usc in u:
            #object might be specified in the POST data, if obj specific data in form
            obj_id = request.POST.get('object_pk', None)
            ctype_id = request.POST.get('content_type', None)
            #if the object is not specificed in POST or this UserSaltCache has no associated ModelCache
            if obj_id is None or not usc.object_specific:
                ctype_id = paramdict.get('TYPE_KEY', None)
                obj_id = paramdict.get('OBJ_KEY', None)
            #get the object related to USC
            obj = get_object_or_none(ctype_id, obj_id)
            div_id = usc.div_id
            #if no ModelCache, then there are multiple elements on one page and we need to specify via div_id
            if usc.object_specific:
                div_id += obj_id
            if not usc.is_recursive:
                render = usc.render(RequestContext(request, {'dimension': paramdict.get('DIM_KEY', 'n'),
                                'object': obj, 'user': user, 'csrf_string': csrf_t,
                                'sort_type': paramdict.get('CTYPE_KEY', '')}))
                rendered_list.append({'obj_pk': obj_id, 'usc_pk': usc.pk, 'toggle': usc.is_toggle,
                                        'div': div_id, 'type': usc.jquery_cmd, 'html': render})
            else:
                #if it's recursive we need to also render all the children USCs
                recursive_list = usc.render(RequestContext(request, {'dimension': paramdict.get('DIM_KEY', 'n'),
                        'object': obj, 'user': user, 'csrf_string': csrf_t, 'sort_type': paramdict.get('CTYPE_KEY', '')}))
                for html, pk in recursive_list:
                    rendered_list.append({'obj_pk': obj_id, 'usc_pk': usc.pk, 'toggle': usc.is_toggle, 'div': div_id, 'type': usc.jquery_cmd, 'html': html})

            #NOW we must update all the c#!landingorresponding lists affected by this in the background: args, comments, etc.
            #deferred.defer(commit_update, None, key)
        return rendered_list, paramdict


def get_cache_or_render(user, key, empty, forcerender=False, request=None):
    """
    get_cache_or_render is required for objects to be returned by
    AJAX requests based on the type of object. This pre-renders
    content so that it is quickly accessible using the oa_cache
    models to interface with templates and div ids derived from css.
    This allows designers to still maintain what templates are pre-rendered
    to improve response time.

    Forms cannot be rendered in this way, as the POST request is sent
    to pirate_core.views.welcome_page, the root of www.openassembly.org/
    **instead we use JS method adObject in detail_dyn.html

    To overcome this only specified cached content in:
        src/pirate_core/templatetags/pp_url/TEMPLATE_DICT
    """
    #init
    tot_items = None
    if key is not None:
        key, rendertype, paramdict = interpret_hash(key)
    rendered_list = []
    load_last = []

    #get the obj if it exists
    ctype_id = paramdict.get('TYPE_KEY', None)
    obj_id = paramdict.get('OBJ_KEY', None)
    dimension = paramdict.get('DIM_KEY', None)
    scroll_to = paramdict.get('SCROLL_KEY', None)
    phase = paramdict.get('PHASE_KEY', None)
    try:
        obj = get_object_or_none(ctype_id, obj_id)
    except:
        return {'rendered_list': [{'html': render_to_string('dead_link.html'), 'ctype_id': ctype_id, 'obj_id': obj_id, 'div': '#content', 'type': 'html'}],
                 'paramdict': {}, 'render': True}
    if dimension is not None and not empty:
        render = False
    else:
        render = True
    #allows hardlinking to slugs: TEMP
    if rendertype == 'community':
        t = Topic.objects.get(slug=dimension)
        obj_id = t.pk
        ctype_id = ContentType.objects.get_for_model(t).pk
        dimension = 'n'
        rendertype = 'list'
        key = '%s/_o%s/_t%s/_dn/_s0/_e20' % (rendertype, obj_id, ctype_id)
        key, rendertype, paramdict = interpret_hash(key)
        obj = get_object_or_none(ctype_id, obj_id)

    #model specific code: if this is an item or user render that obj first
    try:
        m = ModelCache.objects.get(content_type=rendertype, main=True)
        u = UserSaltCache.objects.filter(model_cache=m.pk)
    except:
        m = None
        u = []
    if (rendertype == 'item' or rendertype == 'user' or rendertype == 'arpv') and render:
        if rendertype == 'user':
            forcerender = True
    if m is not None:
        contextual = {'user': user,
                    'dimension': paramdict.get('DIM_KEY', None),
                    'start': paramdict.get('START_KEY', 0), 'end': paramdict.get('END_KEY', 20)}
        #if theres no obj, specify the user as the main object
        if obj is not None:
            contextual['object'] = obj
        else:
            contextual['object'] = user

        rendered_list.append({'div': m.div_id,
            'type': 'html', 'html': m.render(contextual,
                    forcerender=True)})

    if request is not None:
        csrf_val = request.COOKIES.get('csrftoken', None)
        csrf_t = "<div style='display:none'><input type='hidden' value='" + str(csrf_val) + "' name='csrfmiddlewaretoken'></div>"
    else:
        csrf_t = ''

    kwargs = {}

    #list specific code:loads after model so detailed content is loaded first
    #if we aren't renderind the main content, we only want to render the list associated with scrolling
    ###Warning: this breaks if you try to display two lists on one page
    if dimension:
        lists = ListCache.objects.filter(content_type=rendertype, template=dimension)
    if not dimension or lists.count() == 0:
        lists = ListCache.objects.filter(content_type=rendertype, default=True)
    for l in lists:
        m_pk = l.model_cache
        lm = ModelCache.objects.get(pk=m_pk)
        #if we aren't forcerendering, try to get rendered_list from memcache
        renders = None
        if not forcerender:
            #renders[0] -> rendered_list | renders[1] -> cached_list | renders[2] -> tot_items
            renders = memcache.get(key + str(l.pk))
        if renders is None or forcerender:
            renders = []
            #get list of objects to be rendered
            cached_list, tot_items = l.get_or_create_list(key, paramdict, forcerender=forcerender)
            for li in cached_list:
                #render each object in the list
                html = lm.render({'object': li, 'dimension': dimension}, forcerender=forcerender)
                renders.append({'div': lm.div_id, 'html': html, 'type': lm.jquery_cmd})

            memcache.set(str(key) + str(l.pk), (renders, cached_list, tot_items))
        else:
            renders, cached_list, tot_items = renders
        rendered_list.extend(renders)

        #add usersaltcache if there is request data
        if request is not None:
            #Get Dybamic inputs not linked to a user
            lu = UserSaltCache.objects.filter(model_cache=lm.pk, opposite=False, load_last=False, **kwargs)
            for usc in lu:
                rendered_list.append({'div': usc.div_id, 'type': usc.jquery_cmd, 'html':
                                    usc.render(RequestContext(request, {'dimension': paramdict.get('DIM_KEY', None),
                                    'object': obj, 'user': user, 'phase': phase, 'sort_type': paramdict.get('CTYPE_KEY', '')}))})

            sp = UserSaltCache.objects.filter(model_cache=lm.pk, object_specific=True, **kwargs)
            for li in cached_list:
                #user requested this, not auto-update. generate user specific html
                for usc in sp:
                    if not usc.is_recursive:
                        try:
                            rendered_list.append({'div': usc.div_id + str(li.pk), 'type': usc.jquery_cmd, 'html':
                            usc.render(RequestContext(request, {'dimension': paramdict.get('DIM_KEY', 'n'),
                            'object': li, 'user': user, 'phase': phase, 'csrf_string': csrf_t, 'sort_type': paramdict.get('CTYPE_KEY', '')}))})
                        except:
                            raise ValueError(str(li) + ' : ' + str(usc))
                    else:
                        #if it's recursive we need to also render all the children USCs
                        recursive_list = usc.render(RequestContext(request, {'dimension': paramdict.get('DIM_KEY', 'n'),
                                'object': li, 'user': user, 'csrf_string': csrf_t, 'sort_type': paramdict.get('CTYPE_KEY', '')}))
                        for html, pk in recursive_list:
                            rendered_list.append({'div': usc.div_id + str(pk), 'type': usc.jquery_cmd, 'html': html})

            #now add all the UserSaltCache objects from this page
            #THIS REQUIRES A REQUEST OBJECT FO' CSRF
            for usc in u:
                rendered_list.append({'div': usc.div_id, 'type': usc.jquery_cmd, 'html':
                            usc.render(RequestContext(request, {'dimension': paramdict.get('DIM_KEY', None),
                                'object': obj, 'user': user, 'phase': phase, 'csrf_string': csrf_t, 'sort_type': paramdict.get('CTYPE_KEY', '')}))})
            #load last for list caches
            lu = UserSaltCache.objects.filter(model_cache=lm.pk, load_last=True, **kwargs)
            for usc in lu:
                load_last.append({'div': usc.div_id, 'type': usc.jquery_cmd, 'html':
                                    usc.render(RequestContext(request, {'dimension': paramdict.get('DIM_KEY', None),
                                    'object': obj, 'user': user, 'phase': phase, 'sort_type': paramdict.get('CTYPE_KEY', '')}))})

        #USER SALT CACHCES WITH DYNAMIC RESPONSES ARE DONE
        if tot_items is not None:
            r = UserSaltCache.objects.filter(model_cache=lm.pk, div_id="#rangelist")
            for usc in r:
                rangelist = get_rangelist(paramdict.get('START_KEY', 0), paramdict.get('END_KEY', 20), tot_items)
                html = usc.render(RequestContext(request, {'rangelist': rangelist,
                        'start': paramdict.get('START_KEY', 0), 'end': paramdict.get('END_KEY', 20),
                        'dimension': paramdict.get('DIM_KEY', None), 'object': obj, 'sort_type': paramdict.get('CTYPE_KEY', '')}))
                rendered_list.append({'div': '#content', 'phase': phase, 'type': usc.jquery_cmd, 'html': html})
    if rendered_list == []:
        context = RequestContext(request, {'search': paramdict.get('SEARCH_KEY', ''),
                            'dimension': paramdict.get('DIM_KEY', None),
                             'user': user, 'csrf_string': csrf_t})
        if obj is not None:
            context['object'] = obj
        val = render_to_string(rendertype + '.html', context)
        rendered_list = [{'div': '#content', 'html': val, 'type': 'html'}]
    #render all the user salt caches associated with this listindex.html#topics/_s0/_e20/_dh
    #i.e. the Sort By: is a user salt cache
    lu = UserSaltCache.objects.filter(opposite=True, **kwargs)
    if m is not None:
        #exclude if model is available
        lu = lu.exclude(model_cache=m.pk)
    for usc in lu:
        rendered_list.append({'div': usc.div_id,  'phase': phase, 'type': usc.jquery_cmd, 'html': usc.render({'request': request, 'object': obj, 'user': user})})
    if m is not None:
        r = UserSaltCache.objects.filter(model_cache=m.pk, load_last=True, **kwargs)
        for usc in r:
            html = usc.render(RequestContext(request, {
                    'dimension': dimension, 'object': obj, 'sort_type': paramdict.get('CTYPE_KEY', '')}))
            rendered_list.append({'div': usc.div_id,  'phase': phase, 'type': usc.jquery_cmd, 'html': html})
    rendered_list.extend(load_last)
    return {'rendered_list': rendered_list, 'paramdict': paramdict, 'render': render, 'scroll_to': scroll_to}


"""
Automatically updates ranked list of different views accessed,
to reduce latency

In the future this update will be dynamic
conditional on the activity of
that page view.#list/_s0/_e20/_dhn

"""


def commit_update(user_pk, key):
    ##TODO: bad patch here, somethings storing keys incorrectly, trach it down and kill it
    if key[0] == '#':
        key = key[1:]
    if key[0] == '#':
        key = key[1:]
    prop = get_cache_or_render(user_pk, key, True, forcerender=True, request=None)


def update_ranks(request):
    codes = memcache.get("rank_update_codes")
    if codes is None:
        codes = {}
        memcache.add("rank_update_codes", codes, 60)
        goto = '/200.html'
        return HttpResponseRedirect(goto)
    else:
        for key, arg_dict in codes.items():
                #deferred.defer(commit_update, None, key, _countdown=60)
                pass
        goto = '/200.html'
        return HttpResponseRedirect(goto)


def load_page(request):
    """
This is the main function of OpenAssembly. It sends AJAX requests to the oa_cache
models, each responsible for rendering. oa_cache is responsible for the rendering and caching of lists, items,
and user information. Using an AJAX GET/POST and caching system has greatly
decreased the latency of the system.

*Each cache is specified by a unique 'key' value and corresponding 'paramdict' that
 is passed around the various functions. Some parameters of the system include
 START, END, DIMENSION, SCROLL_TO, and more parameters can be added as needed.

"""
    if request.method == 'GET':
        data = {'output': []}
        hashed = request.GET.get('hash', None)
        if hashed is None:
            hashed = ''
        empty = request.GET.get('empty', None)
        hashed = hashed.replace(DOMAIN, '')
        if hashed == '/' and empty != 'false' and not request.user.is_authenticated():
            hashed = '/p/landing'
        elif hashed == '/' and empty != 'false' and request.user.is_authenticated():
            hashed = '/p/landing'
            #need to make this some sort of home feed for user
        if hashed[0:2] == '/p':
            props = get_cache_or_render(request.user, hashed, empty, request=request, forcerender=True)
            if props['render']:
                #if the c
                props['rendered_list'].insert(0, {'div': '#content', 'type': 'html', 'html': ''})
            for d in props['rendered_list']:
                data['output'].append(d)
            #deferred.defer(create_view, request.user.username, request.META.get('REMOTE_ADDR'), props['paramdict'].get('OBJ_ID', None), _countdown=10)
            data['FAIL'] = False
            if 'SCROLL_KEY' in props['paramdict']:
                data['scroll_to'] = '#' + props['paramdict']['SCROLL_KEY']
        else:
            data['FAIL'] = hashed
        if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
                return HttpResponse(simplejson.dumps(data),
                                    mimetype='application/json')
    elif request.method == 'POST':
        data = {'FAIL': False}
        #we just want to update the request changes and return what is rendered
        q = QueryDict('', mutable=True)
        p = request.POST.copy()
        hashed = p.pop('hash', '')[0]
        for k, v in p.items():
            #cut off javascript 'form[...]'' in key to get ...
            q[k[5:-1]] = v
        q['hash'] = hashed
        request.POST = q
        div = request.POST['form_id']
        rendered_list, param_dict = post_cache(request.user, hashed, div, request)

        data['output'] = rendered_list
        data['debug'] = div
        #now we want to post to the cache and re-render the appropriate part of the page
        if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
                return HttpResponse(simplejson.dumps(data),
                                    mimetype='application/json')


def load_usersaltcache(request):
    """
This is the main function of OpenAssembly. It sends AJAX requests to the oa_cache
models, each responsible for rendering. oa_cache is responsible for the rendering and caching of lists, items,
and user information. Using an AJAX GET/POST and caching system has greatly
decreased the latency of the system.

*Each cache is specified by a unique 'key' value and corresponding 'paramdict' that
 is passed around the various functions. Some parameters of the system include
 START, END, DIMENSION, SCROLL_TO, and more parameters can be added as needed.

"""
    if request.method == 'GET':
        data = {'output': []}
        hashed = request.GET.get('hash', None)
        div = request.GET.get('div', None)
        try:
            user = User.objects.get(pk=request.GET.get('user', None))
        except:
            user = None
        key, rendertype, paramdict = interpret_hash(hashed)

        ctype_id = request.GET.get('ctype_pk', None)
        obj_id = request.GET.get('obj_pk', None)
        obj = get_object_or_none(ctype_id, obj_id)

        usc = UserSaltCache.objects.get(div_id=div)
        render = {'div': usc.div_id, 'type': usc.jquery_cmd, 'html':
                    usc.render(RequestContext(request, {'dimension': paramdict.get('DIM_KEY', None),
                    'object': obj, 'user': user, 'sort_type': paramdict.get('CTYPE_KEY', '')}))}

        data['output'] = [render]
        #deferred.defer(create_view, request.user.username, request.META.get('REMOTE_ADDR'), props['paramdict'].get('OBJ_ID', None), _countdown=10)
        data['FAIL'] = False

        if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
                return HttpResponse(simplejson.dumps(data),
                                    mimetype='application/json')


def load_page_ret(request, ts, url, c):
    response = c.get(url)
    return response


def nuke_memcache(request):
    if request.user.is_authenticated and request.user.is_staff:
        codes = memcache.get("rank_update_codes")
        if codes is None:
            codes = {}
            memcache.add("rank_update_codes", codes, 60)
            goto = '/200.html'
            return HttpResponseRedirect(goto)
        else:
            for key, arg_dict in codes.items():
                memcache.delete(key)
            goto = '/200.html'
            return HttpResponseRedirect(goto)
    goto = '/200.html'
    return HttpResponseRedirect(goto)
