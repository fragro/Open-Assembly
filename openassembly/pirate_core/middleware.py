from django.contrib.contenttypes.models import ContentType
from django.template import add_to_builtins


TYPE_KEY = "t-"
OBJ_KEY = "o-"
START_KEY = "s-"
END_KEY = "e-"
DIM_KEY = "d-"
SCROLL_KEY = "c-"
RETURN_KEY = "z-"
SIMPLEBOX_KEY = "i-"
SEARCH_KEY = "r-"
CTYPE_KEY = "l-"
PHASE_KEY = "p-"
S_KEY = "i-"
STR_KEY = "k-"


def human_readable_dim(d):
    if d == 'h':
        return 'Hot'
    elif d == 'c':
        return 'Controversial'
    elif d == 'n':
        return 'New'


class UrlMiddleware(object):
    """
    This class works in conjunction with the pp_url tag to populate requests with
    a model instance and/or a numerical range that can be used in pagination.
    This also maintains a queue of recently visited urls, that can be used as 'breadcrumbs'
        for ease in navigation.
    """

    def process_request(self, request):

        content_type_id = request.GET.get(TYPE_KEY)
        obj_id = request.GET.get(OBJ_KEY)
        start = request.GET.get(START_KEY)
        end = request.GET.get(END_KEY)
        dim = request.GET.get(DIM_KEY)
        scroll_to = request.GET.get(SCROLL_KEY)
        returnurl = request.GET.get(RETURN_KEY)
        simplebox = request.GET.get(SIMPLEBOX_KEY)
        search = request.GET.get(SEARCH_KEY)
        str_key = request.GET.get(STR_KEY)

        if search is not None:
            request.search = search

        if simplebox is not None:
            request.simplebox = simplebox

        if content_type_id is not None and obj_id is not None:
            content_type = ContentType.objects.get(pk=content_type_id)
            try:
                request.object = content_type.get_object_for_this_type(pk=obj_id)
            except:
                pass

        if str_key is not None:
            try:
                cached_type = ContentType.objects.get(app_label="pirate_ranking", model="cached_url")
                cached_model = cached_type.model_class()
                cached = cached_model.objects.get(slug=str_key)
                content_type = ContentType.objects.get(pk=cached.ctype_pk)
                request.object = content_type.get_object_for_this_type(pk=cached.obj_pk)
            except:
                pass

        if start is not None and end is not None:
            request.start = int(start)
            request.end = int(end)
            rangelist = []
            div = int(start) / 100.0
            multiple = round(div)
            start_range = int(100 * multiple)
            n = 1
            for itr in range(start_range, start_range + 100, 20):
                rangelist.append([itr, itr + 20, n])
                n += 1
            request.rangelist = rangelist

        if returnurl is not None:
            request.returnurl = returnurl

        if dim is not None:
            request.dimension = dim

        if scroll_to is not None:
            request.scroll_to = True
            request.scroll_to_div = scroll_to

        if obj_id is not None:
            pass
            #deferred.defer(create_view, request.user.username, request.META.get('REMOTE_ADDR'), obj_id, _countdown=10)
        """
        ##TODO:
        ##THIS SHOULD BE REWRITTEN TO ONLY TAKE INTO ACCOUNT WHAT WE WANT TO SAVE
        request_path = request.get_full_path()
        name = request_path
        if request_path != '/favicon.ico' and request_path[0:7] != '/submit' and request_path not in ['update_video_votes',
                    'add_video_vote', '/starvote/', '/logout/', '/spectrumvote/', '/'] and request_path[0:6] not in ['/reset',
                                                                                '/uploa'] and request.path[0:9] != '/password':
                try: request.session['currently_visiting']
                except: request.session['currently_visiting'] = request_path
                if request.session['currently_visiting'] != request_path:
                    try:
                        visit_list = list(request.session['last_visited'])
                    except:
                        visit_list = []
                    if len(visit_list) >= 8:
                        try: visit_list.pop(0)
                        except: pass #no visit_list
                    try: #name logic goes here
                        #you have request.object and content_type
                        if request.path[0:4] == '/iss': #for issue list
                                icon = str(request.dimension).upper()[0]
                                if content_type_id is not None and obj_id is not None:
                                    t_name = str(request.object.summary) + " issues"
                                else: 
                                    t_nam = "issues"
                                try: name = human_readable_dim(str(request.dimension)) + " " + t_nam
                                except: name = "hot " + t_nam  
                        elif request.path[0:4] == '/top':
                            name = "topics"
                            icon = 'O'
                        elif request.path[0:4] == '/wel':
                            name = "welcome"
                            icon = 'O'
                        elif request.path[0:4] == '/faq':
                            name = 'FAQ'
                            icon = 'O'
                        elif content_type_id is not None and obj_id is not None:
                            if request.path[0:4] == '/det': #for details
                                name = str(request.object.summary)
                                ctype = ContentType.objects.get(pk=content_type_id)
                                icon = str(ctype)[0].upper()
                            elif request.path[0:4] == '/use':
                                name = str(request.object.username)
                                icon = 'U'
                    except:
                        name = None
                    try:
                        if name != None and name != request_path and (name, request_path,datetime.datetime.now(),icon) not in visit_list:
                            try:
                                if visit_list[-1][0] != name: visit_list.append((name, request_path,datetime.datetime.now(),icon))
                            except: visit_list.append((name, request_path, datetime.datetime.now(),icon))
                    except KeyError: pass #first visit
                    request.session['last_visited'] = visit_list
        if request_path != '/favicon.ico' and request_path[0:7] != '/submit' and request_path not in ['update_video_votes','add_video_vote','/starvote/', '/logout/', '/spectrumvote/','/'] and request_path[0:6] not in ['/reset','/uploa'] and request.path[0:9] != '/password':
            request.session['currently_visiting'] = request_path
        """


class AddToBuiltinsMiddleware(object):
    def process_request(self, request):
        # This adds all tags registered separately through native_tags to the builtins
        add_to_builtins('native_tags.templatetags.native')
