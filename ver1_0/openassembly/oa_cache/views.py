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
from django.shortcuts import redirect
from settings import DOMAIN
from oa_cache.tasks import track_visitors
import random
import settings
import BeautifulSoup
from types import ListType
from collections import defaultdict
import settings


def get_object_or_none(ctype_id, obj_id):
    """
Returns object with ID and ContentType ID
"""
    if ctype_id is not None and obj_id is not None and ctype_id != '' and obj_id != '':
        try:
            content_type = ContentType.objects.get(pk=ctype_id)
        except Exception, e:
            raise e
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

        jsonval = simplejson.loads(se)
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
                    if s.key_specific:
                        div = s.div_id + obj.get_absolute_url().replace('/', '')
                    elif s.object_specific:
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
        u = UserSaltCache.objects.filter(div_id='#' + div)

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
            retkey = key.replace('/', '')
            if not usc.is_recursive:
                render = usc.render(RequestContext(request, {'dimension': paramdict.get('DIM_KEY', 'n'),
                                'key': retkey, 'object': obj, 'user': user, 'csrf_string': csrf_t,
                                'sort_type': paramdict.get('CTYPE_KEY', '')}))
                rendered_list.append({'obj_pk': obj_id, 'usc_pk': usc.pk, 'toggle': usc.is_toggle,
                                        'div': div_id, 'type': usc.jquery_cmd, 'html': render})
            else:
                #if it's recursive we need to also render all the children USCs
                recursive_list = usc.render(RequestContext(request, {'key': retkey, 'dimension': paramdict.get('DIM_KEY', 'n'),
                        'object': obj, 'user': user, 'csrf_string': csrf_t, 'sort_type': paramdict.get('CTYPE_KEY', '')}))
                for html, pk in recursive_list:
                    rendered_list.append({'obj_pk': obj_id, 'usc_pk': usc.pk, 'toggle': usc.is_toggle, 'div': div_id, 'type': usc.jquery_cmd, 'html': html})

            #NOW we must update all the c#!landingorresponding lists affected by this in the background: args, comments, etc.
            #deferred.defer(commit_update, None, key)
        return rendered_list, paramdict


def get_cache_or_render(user, key, empty, forcerender=True, request=None, extracontext={}):
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


    *** There are a lot of repeated prgramming patterns throughout this function and it
        could easily be optimized
    """
    #init
    tot_items = None
    if key is not None:
        key, rendertype, paramdict = interpret_hash(key)
    rendered_list = []
    load_last = []
    counts = {}

    #need to determine the computational load of adding all the settings dict to the context, if any. Should be a heavier memory load at most, but
    #I don't see how this could slow down the cpu necessarily if we are using hashing
    extracontext.update({'template': rendertype, 'user': user, 'key': key.replace('/', ''), 'settings': settings})

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
            contextual['object'] = rendertype.replace('_', ' ')
        contextual.update(extracontext)
        #set obj pk
        try:
            obj_pk = contextual['object'].pk
        except:
            obj_pk = m.content_type
        rendered_list.append({'obj_pk': obj_pk, 'div': m.div_id,
            'type': m.jquery_cmd, 'html': m.render(RequestContext(request, contextual))})
        usc = UserSaltCache.objects.filter(model_cache=m.pk, load_last=False)
        for usc in u:
            if usc.object_specific:
                rendered_list.append({'obj_pk': obj_pk, 'div': usc.div_id + obj_pk, 'type': usc.jquery_cmd, 'html':
                       usc.render(RequestContext(request, contextual))})
            else:
                rendered_list.append({'obj_pk': obj_pk, 'div': usc.div_id, 'type': usc.jquery_cmd, 'html':
                       usc.render(RequestContext(request, contextual))})

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
            sp = UserSaltCache.objects.filter(model_cache=lm.pk, object_specific=True, **kwargs)

            if len(cached_list) == 0:
                renders.append({'div': lm.div_id, 'html': '', 'type': lm.jquery_cmd})
            for li in cached_list:
                #render each object in the list
                if li != None:
                    context = {'div': lm.div_id, 'object': li, 'dimension': dimension}
                    context.update(extracontext)
                    html = lm.render(context, forcerender=forcerender)
                    if lm.object_specific:
                        renders.append({'div': lm.div_id + str(obj.pk), 'html': html, 'type': lm.jquery_cmd})
                    else:
                        renders.append({'div': lm.div_id, 'html': html, 'type': lm.jquery_cmd})
                if li != None:
                    try:
                        context = {'dimension': paramdict.get('DIM_KEY', 'n'),
                                'object': li, 'obj_pk': li.pk, 'user': user,
                                'phase': phase, 'csrf_string': csrf_t,
                                'sort_type': paramdict.get('CTYPE_KEY', '')}
                    except:
                            context = {'dimension': paramdict.get('DIM_KEY', 'n'),
                                'object': li, 'obj_pk': li[0].pk, 'user': user,
                                'phase': phase, 'csrf_string': csrf_t,
                                'sort_type': paramdict.get('CTYPE_KEY', '')}
                    context.update(extracontext)
                    #user requested this, not auto-update. generate user specific html
                    for usc in sp:
                        if not usc.is_recursive:
                            retdiv = usc.div_id + str(li.pk)
                            renders.append({'div': retdiv, 'type': usc.jquery_cmd, 'html':
                            usc.render(RequestContext(request, context))})
                        else:
                            #if it's recursive we need to also render all the children USCs
                            recursive_list = usc.render(RequestContext(request, context))
                            for html, pk in recursive_list:
                                renders.append({'div': usc.div_id + str(pk), 'type': usc.jquery_cmd, 'html': html})  
            memcache.set(str(key) + str(l.pk), (renders, cached_list, tot_items))
        else:
            renders, cached_list, tot_items = renders
        rendered_list.extend(renders)
        counts[rendertype] = tot_items
        #add usersaltcache if there is request data
        if request is not None:
            #Get Dybamic inputs not linked to a user
            lu = UserSaltCache.objects.filter(model_cache=lm.pk, object_specific=False, opposite=False, load_last=False, **kwargs)
            context = {'dimension': paramdict.get('DIM_KEY', None),
                                    'user': user, 'phase': phase,
                                    'sort_type': paramdict.get('CTYPE_KEY', '')}
            if obj is not None:
                context.update({'object': obj, 'obj_pk': obj.pk})
            context.update(extracontext)
            for usc in lu:
                rendered_list.append({'div': usc.div_id, 'type': usc.jquery_cmd, 'html':
                                    usc.render(RequestContext(request, context))})

            #now add all the UserSaltCache objects from this page
            #THIS REQUIRES A REQUEST OBJECT FO' CSRF
            context = {'dimension': paramdict.get('DIM_KEY', None),
                                'user': user, 'phase': phase,
                                'csrf_string': csrf_t, 'sort_type': paramdict.get('CTYPE_KEY', '')}
            if obj is not None:
                context.update({'object': obj, 'obj_pk': obj.pk})
            context.update(extracontext)
            #for usc in u:
            #    rendered_list.append({'test': 'test', 'obj_pk': obj.pk, 'div': usc.div_id, 'type': usc.jquery_cmd, 'html':
            #                usc.render(RequestContext(request, context))})
            #load last for list caches
            lu = UserSaltCache.objects.filter(model_cache=lm.pk, load_last=True, **kwargs)
            for usc in lu:
                load_last.append({'obj_pk': obj.pk, 'div': usc.div_id, 'type': usc.jquery_cmd, 'html':
                                    usc.render(RequestContext(request, context))})

        #USER SALT CACHCES WITH DYNAMIC RESPONSES ARE DONE
        if tot_items is not None:
            r = UserSaltCache.objects.filter(model_cache=lm.pk, div_id="#rangelist")
            for usc in r:
                rangelist = get_rangelist(paramdict.get('START_KEY', 0), paramdict.get('END_KEY', 20), tot_items)
                html = usc.render(RequestContext(request, {'rangelist': rangelist,
                        'start': paramdict.get('START_KEY', 0), 'end': paramdict.get('END_KEY', 20),
                        'dimension': paramdict.get('DIM_KEY', None), 'object': obj, 'sort_type': paramdict.get('CTYPE_KEY', '')}))
                rendered_list.append({'div': '#pages', 'phase': phase, 'type': usc.jquery_cmd, 'html': html})
    if rendered_list == []:
        context = {'search': paramdict.get('SEARCH_KEY', ''),
                            'dimension': paramdict.get('DIM_KEY', None),
                             'user': user, 'csrf_string': csrf_t, 'template': rendertype}
        context.update(extracontext)
        context = RequestContext(request, context)
        if obj is not None:
            context['object'] = obj
        else:
            context['object'] = rendertype.replace('_', ' ')
        if rendertype != '':
            #first try for free floating usersaltcache forms...
            usc = UserSaltCache.objects.filter(template=rendertype + '.html')
            for u in usc:
                obj_pk = random.randint(-1000, 10000)
                rendered_list.append({'div': u.div_id, 'type': u.jquery_cmd, 'obj_pk': obj_pk, 'html':
                            u.render(context)})
                cached = UserSaltCache.objects.filter(model_cache=u.pk)
                for c in cached:
                    rendered_list.append({'div': c.div_id, 'type': c.jquery_cmd, 'obj_pk': obj_pk, 'html':
                            c.render(context)})
            if rendered_list == []:
                context['request'] = request
                val = render_to_string(rendertype + '.html', context)
                if obj is not None:
                    rendered_list = [{'div': '#pages', 'html': val, 'type': 'append', 'obj_pk': obj.pk}]
                else:
                    rendered_list = [{'div': '#pages', 'html': val, 'type': 'append'}]

    #render all the user salt caches associated with this listindex.html#topics/_s0/_e20/_dh
    #i.e. the Sort By: is a user salt cache
    lu = UserSaltCache.objects.filter(opposite=True, **kwargs)
    if m is not None:
        #exclude if model is available
        lu = lu.exclude(model_cache=m.pk)
    for usc in lu:
        rendered_list.append({'div': usc.div_id, 'obj_pk': obj_pk,  'phase': phase, 'type': usc.jquery_cmd, 'html': usc.render({'request': request, 'object': obj, 'user': user})})
    if m is not None:
        r = UserSaltCache.objects.filter(model_cache=m.pk, load_last=True, **kwargs)
        context = {'dimension': dimension, 'object': obj,
            'obj_pk': obj_pk, 'sort_type': paramdict.get('CTYPE_KEY', '')}
        context.update(extracontext)
        for usc in r:
            html = usc.render(RequestContext(request, context))
            rendered_list.append({'div': usc.div_id,  'phase': phase, 'type': usc.jquery_cmd, 'html': html})
    rendered_list.extend(load_last)
    return {'counts': counts, 'object': obj, 'rendered_list': rendered_list, 'paramdict': paramdict, 'render': render, 'scroll_to': scroll_to, 'rendertype': rendertype}


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
        request.session.set_expiry(0)
        data = {'output': []}
        hashed = request.GET.get('hash', None)
        width = request.GET.get('width', None)
        height = request.GET.get('height', None)
        extracontext = {'width': width, 'height': height, 'DOMAIN': DOMAIN}

        if hashed is None:
            hashed = ''
        empty = request.GET.get('empty', None)
        hashed = hashed.replace(DOMAIN, '')
        data['key'] = hashed.replace('/', '')
        if hashed == '/' and empty != 'false' and not request.user.is_authenticated():
            hashed = '/p/landing'
        elif hashed == '/' and empty != 'false' and request.user.is_authenticated():
            hashed = '/p/landing'
            #need to make this some sort of home feed for user
        if hashed[0:2] == '/p':
            props = get_cache_or_render(request.user, hashed, empty, request=request, forcerender=False, extracontext=extracontext)
            for d in props['rendered_list']:
                data['output'].append(d)
            if 'OBJ_KEY' in props['paramdict']:
                obj_pk = props['paramdict']['OBJ_KEY']
            else:
                obj_pk = None
            create_view.apply_async(args=[request.user, request.META.get('REMOTE_ADDR'), obj_pk, hashed, props['rendertype']])
            data['FAIL'] = False
            data['rendertype'] = props['rendertype']
            if 'SCROLL_KEY' in props['paramdict']:
                data['scroll_to'] = '#' + props['paramdict']['SCROLL_KEY']
        else:
            #data['FAIL'] = hashed
            return HttpResponse(simplejson.dumps({'redirect': hashed}),
                                    mimetype='application/json')
        #track visitors
        track_visitors(request)
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
        if usc.object_specific:
            div_id = usc.div_id + obj_id
        else:
            div_id = usc.div_id
        render = {'div': div_id, 'type': usc.jquery_cmd, 'html':
                    usc.render(RequestContext(request, {'dimension': paramdict.get('DIM_KEY', None),
                    'object': obj, 'user': user, 'sort_type': paramdict.get('CTYPE_KEY', '')}))}

        data['output'] = [render]
        #deferred.defer(create_view, request.user.username, request.META.get('REMOTE_ADDR'), props['paramdict'].get('OBJ_ID', None), _countdown=10)
        data['FAIL'] = False

        if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
                return HttpResponse(simplejson.dumps(data),
                                    mimetype='application/json')


def render_hashed(request, key, user, extracontext={}):
    ###Need to get all of the rendered html
    ###and integrate via Beautiful
    if 'TYPE' in extracontext:
        htmlrender = extracontext['TYPE'] == 'HTML'
    else:
        htmlrender = 'JS'
    if key is None:
        key = request.META['PATH_INFO']
    empty = True
    if user is None:
        user = request.user
    retdict = get_cache_or_render(user, key, empty, forcerender=True, request=request, extracontext=extracontext)
    rendered_list = retdict['rendered_list']
    ret = defaultdict(list)
    for i in rendered_list:
        for k,v in i.items():
            if k != 'html': print k + ' '+ str(v)
        if type(i['html']) == ListType:
            for v, k in i['html']:
                soup = BeautifulSoup.BeautifulSoup(v)
                if i['type'] == 'html':
                    ret[i['div']] = [soup]
                elif i['type'] == 'append':
                    ret[i['div']].append(soup)
        else:
            #print i['div'] + ' : ' + i['type']
            soup = BeautifulSoup.BeautifulSoup(i['html'])
            if '#pages' in ret and i['div'] != '#tab_ruler' and i['type'] != 'html':
                text = ret['#pages'][0].find('div', {'id': i['div'][1:]})
                #print text
                if text is not None:
                    text.insert(0, BeautifulSoup.NavigableString(i['html']))
            elif i['type'] == 'html':
                ret[i['div']] = [soup]
            elif i['type'] == 'append':
                ret[i['div']].append(soup)
            elif i['type'] == 'prepend':
                ret[i['div']].insert(0,soup)
            else:
                print i['type']
                text = ret[i['type']][len(ret[i['type']])-1].find('div', {'id': i['div'][1:]})
                #print text
                if text is not None:
                    text.insert(0, BeautifulSoup.NavigableString(i['html']))
    rendertype = retdict['rendertype']
    final = {}
    for k, v in ret.items():
        r = ''
        for val in v:
            r += val.prettify()
        if htmlrender:
            final[k[1:]] = r
        else:
            final[k] = r
    return {'renders': final, 'object': retdict['object'], 'rendertype': rendertype, 'counts': retdict['counts']}


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
