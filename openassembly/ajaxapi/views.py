# Create your views here.
from pirate_consensus.models import Consensus, RatingVote, UpDownVote, VideoVote
from django.utils import simplejson
from django.http import HttpResponse, HttpResponseRedirect
from pirate_sources.models import URLSource
from tagging.models import Tag
import datetime
from django.shortcuts import get_object_or_404,redirect
from django.contrib.contenttypes.models import ContentType
from pirate_flags.models import Flag, UserFlag
from django.contrib.auth.models import User
from pirate_badges.models import check_badges

from pirate_topics.models import Topic, MyGroup
from pirate_messages.models import Notification

from pirate_reputation.models import ReputationEvent

from django.template.loader import render_to_string

from pirate_social.models import Subscription

from oa_platform.models import Platform, PlatformDimension
from oa_cache.models import interpret_hash, build_hash
from oa_cache.views import update_ranks

from django.template import RequestContext
from django.shortcuts import render_to_response

from pirate_ranking.models import vote_created_callback
from tagging.models import TaggedItem
from pirate_core.templatetags.tag_helpers import get_recommended_tag_list,get_link_tag_list

from pirate_signals.models import aso_rep_event,aso_rep_delete,relationship_event,delete_relationship_event, update_agent
from pirate_reputation.models import ReputationDimension

from oa_filmgenome.models import FilmIdea
import search

from search.views import live_search_results

from oa_verification.models import EmailVerification


def live_search(request):
    return live_search_results(request, FilmIdea,
     result_item_formatting=lambda post:
        {'value': u'<div>%s</div>' % (post.summary),
        'result': post.summary, })


def search_posts(request):
    posts = None
    if 'query' in request.GET:
        posts = search(FilmIdea, request.GET['query'])
    return redirect("/index.html#search_results")
    return render_to_response('search_results.html',
        {'posts': posts}, context_instance=RequestContext(request))


def add_support(request, pk):
    ###Pirate_social AJAX views
    if request.user.is_authenticated() and request.user.is_active:

        user = User.objects.get(pk=pk)
        c_type = ContentType.objects.get_for_model(user)
        sub = Subscription(subscriber=request.user, subscribee=user,
                            created_dt=datetime.datetime.now())
        sub.save()
        return redirect("/index.html#user/_t" + str(c_type.pk) +
                    "/_o" + str(user.pk))
    else:
        return redirect('/register.html?')


def remove_support(request, pk):
    if request.user.is_authenticated() and request.user.is_active:
        user = User.objects.get(pk=pk)
        c_type = ContentType.objects.get_for_model(user)
        sub = Subscription.objects.get(subscriber=request.user,
                                        subscribee=user)
        sub.delete()
        return redirect("/index.html#user/_t" + str(c_type.pk) +
                        "/_o" + str(user.pk))
    else:
        return redirect('/register.html?')


def change_hash_dim(request):
    if not request.user.is_authenticated() or not request.user.is_active:
        return HttpResponse(simplejson.dumps({'FAIL': True}),
                                mimetype='application/json')

    if request.method == 'GET':
        results = {}
        hashed = request.GET[u'hash'][1:]
        dim = request.GET[u'dim']
        newkey, rtype, d = interpret_hash(hashed)
        d['DIM_KEY'] = dim
        h = build_hash(rtype, d)
        results['new_hash'] = h
        results['FAIL'] = False
    else:
        results = {'FAIL': True}
    if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
        return HttpResponse(simplejson.dumps(results),
                            mimetype='application/json')


def change_hash_ctype(request):
    if not request.user.is_authenticated() or not request.user.is_active:
        return HttpResponse(simplejson.dumps({'FAIL': True}),
                                mimetype='application/json')

    if request.method == 'GET':
        results = {}
        hashed = request.GET[u'hash'][1:]
        if hashed == '':
            topic, is_new = Topic.objects.get_or_create(is_featured=True)
            content_type = ContentType.objects.get_for_model(topic)
            hashed = 'list/_t' + str(content_type.pk) + '/_o' + str(topic.pk) + '/_s0/_e20/_dhn'
        ctype = request.GET[u'dim']
        newkey, rtype, d = interpret_hash(hashed)
        d['CTYPE_KEY'] = ctype
        h = build_hash(rtype, d)
        results['new_hash'] = h
        results['FAIL'] = False
    else:
        results = {'FAIL': True}
    if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
        return HttpResponse(simplejson.dumps(results),
                            mimetype='application/json')


def remove_group(request):
    if not request.user.is_authenticated() or not request.user.is_active:
        return HttpResponse(simplejson.dumps({'FAIL': True}),
                                mimetype='application/json')

    if request.method == 'POST':
        user_pk = int(request.POST[u'user'])
        topic_pk = int(request.POST[u'topic'])

        user = User.objects.get(pk=user_pk)
        topic = Topic.objects.get(pk=topic_pk)

        if request.user == user:
            my = MyGroup.objects.get(topic=topic, user=user)
            my.delete()
            topic.group_members -= 1
            topic.save()
            group_name = topic.pk
            results = {'FAIL': False, 'group': '#' + str(group_name)}
        else:
            results = {'FAIL:': True}
    else:
        results = {'FAIL': True}
    if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
        return HttpResponse(simplejson.dumps(results),
                            mimetype='application/json')


def add_group(request):
    if not request.user.is_authenticated() or not request.user.is_active:
        return HttpResponse(simplejson.dumps({'FAIL': True}),
                                mimetype='application/json')

    if request.method == 'POST':
        user_pk = int(request.POST[u'user'])
        topic_pk = int(request.POST[u'topic'])

        user = User.objects.get(pk=user_pk)
        topic = Topic.objects.get(pk=topic_pk)

        if request.user == user:
            my, is_new = MyGroup.objects.get_or_create(topic=topic, user=user)
            topic.group_members += 1
            topic.save()
            if not is_new:
                results = {'FAIL': True}
            else:
                results = {'FAIL': False, 'group': render_to_string('mygroup.html', {'group': my})}
        else:
            results = {'FAIL:': True}
    else:
        results = {'FAIL': True}
    if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
        return HttpResponse(simplejson.dumps(results),
                            mimetype='application/json')


def add_platform(request):
    if not request.user.is_authenticated() or not request.user.is_active:
        return HttpResponse(simplejson.dumps({'FAIL': True}),
                                mimetype='application/json')

    if request.method == 'POST':
        ctype = int(request.POST[u'ctype'])
        object_pk = int(request.POST[u'object_pk'])

        pd = PlatformDimension.objects.get(pk=ctype)

        pl, is_new = Platform.objects.get_or_create(user=request.user,
                                    dimension=pd)
        #hehe
        planck_length = len(pl.planks)
        if planck_length < pd.num_planks and object_pk not in pl.planks:
            pl.planks.append(object_pk)
            pl.save()
            update_agent.send(sender=pl, type="user", params=[request.user.pk])
            results = {'FAIL': False, 'complete_perc': str(int((planck_length + 1) / float(pd.num_planks) * 100)) + '%'}
        else:
            results = {'FAIL': True}
    else:
        results = {'FAIL': True}
    if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
        return HttpResponse(simplejson.dumps(results),
                            mimetype='application/json')


def remove_platform(request):
    if not request.user.is_authenticated() or not request.user.is_active:
        return HttpResponse(simplejson.dumps({'FAIL': True}),
                                mimetype='application/json')

    if request.method == 'POST':
        ctype = int(request.POST[u'ctype'])
        object_pk = int(request.POST[u'object_pk'])

        pd = PlatformDimension.objects.get(pk=ctype)

        pl, is_new = Platform.objects.get_or_create(user=request.user,
                                    dimension=pd)
        pl.planks.remove(object_pk)
        pl.save()
        update_agent.send(sender=pl, type="user", params=[request.user.pk])
        results = {'FAIL': False, 'complete_perc': str(int(len(pl.planks) / float(pd.num_planks) * 100)) + '%'}
    else:
        results = {'FAIL': True}
    if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
        return HttpResponse(simplejson.dumps(results),
                            mimetype='application/json')


def confirm(request, key):
    if request.user.is_authenticated():
        return redirect("/index.html")
    user_profile = get_object_or_404(EmailVerification,
                                     activation_key=key)
    if user_profile.key_expires < datetime.datetime.today():
        return redirect("/expired.html")
    user_account = user_profile.user
    user_account.is_active = True
    user_account.save()
    update_agent.send(sender=user_account, type="user",
                                params=[user_account.pk])
    return redirect("/index.html#confirm")


#HTML5 video voting functions
def add_video_vote(request):
    if not request.user.is_authenticated()  or not request.user.is_active:
        #needs to popup registration dialog instead
        return HttpResponse(simplejson.dumps({'FAIL': True, 'ERR1':True,'ERR2':False}), #need a better non-auth error here, interferes with view
                                mimetype='application/json')

    if request.method == 'POST':
        """<QueryDict: {u'data[vote][time]': [u'12.582378387451172'], u'data[vote][duration]': [u'207.4702911376953'], u'data[vote][video_id]': [u'2'], u'data[vote][ip_address]': [u'f528764d624db129b32c21fbca0cb8d6'], u'data[vote][keycode]': [u'32']}>"""

        time = float(request.POST.get('data[vote][time]'))
        duration = request.POST.get('data[vote][duration]')
        v_id = request.POST.get('data[vote][video_id]')
        bars = request.POST.get('bars')

        #check to see if this user has already voted in this bucket
        time_interval = (float(duration) / float(bars))
        old_votes = VideoVote.objects.filter(user=request.user, video_id=v_id)
        for v in old_votes:
            if (time > v.time - time_interval and time < v.time) or (time < v.time + time_interval and time > v.time):
                return HttpResponse(simplejson.dumps({'FAIL':True,'ERR1':False,'ERR2':True}),
                            mimetype='application/json')


        new_vote = VideoVote(user=request.user, time=time, duration=duration, video_id=v_id)
        new_vote.save()

        return HttpResponse(simplejson.dumps({'FAIL':False}),
                            mimetype='application/json')


def update_video_votes(request):
    if request.method == 'POST':

        video_id = request.POST.get('video_id')
        duration = float(request.POST.get('duration'))
        bars = int(request.POST.get('bars'))

        votes = VideoVote.objects.filter(video_id=video_id)
        barlist = [0 for i in range(bars + 2)]
        for vote in votes:
            #for each vote calculate bucket and add 1
            barlist[int(float(vote.time / vote.duration) * float(bars + 2))] += 1

        return HttpResponse(simplejson.dumps(str(barlist)),
                            mimetype='application/json')

#DELETE FUNCTIONS
def delete_source(request,object_id, consensus_id):
    obj = get_object_or_404(URLSource, id=object_id)
    obj.delete()
    con = Consensus.objects.get(pk=consensus_id)
    return redirect(con.content_object.get_absolute_url())

#DELETE OBJ
#removes object from the database. There are orphan votes and comments still around.
def delete_object(request):
    if not request.user.is_authenticated() or not request.user.is_active:
        return HttpResponse(simplejson.dumps({'FAIL': True, 'message': 'user inactive or not logged in'}),
                                mimetype='application/json')

    if request.method == 'POST':
        content_type = int(request.POST[u'content_type'])
        object_id = int(request.POST[u'object_id'])
        contype = ContentType.objects.get(pk=content_type)
        cons = Consensus.objects.get(object_pk=object_id)
        mod = contype.model_class()
        obj = mod.objects.get(pk=object_id)
        if not obj.user == request.user:
            if not request.user.is_staff:
                return HttpResponse(simplejson.dumps({'FAIL': True, 'message': 'object user not request user'}),
                                mimetype='application/json')
        #need to delete all the notifications about this
        reps = ReputationEvent.objects.filter(object_id=cons.pk)
        for i in reps:
            i.delete()
        notes = Notification.objects.filter(object_pk=obj.pk)
        for i in notes:
            i.delete()
        notes = Notification.objects.filter(object_pk=cons.pk)
        for i in notes:
            i.delete()
        # now delete the object
        obj.delete()
        user_cons = Consensus.objects.get(object_pk=request.user.pk)
        #delete all votes
        uvote = UpDownVote.objects.filter(parent=cons)
        for i in uvote:
            aso_rep_delete.send(sender=request.user, event_score=1, user=i.user,
                                initiator=request.user, dimension=ReputationDimension.objects.get('Vote'),
                                related_object=i,is_vote=True) # register reputation for voting
            user_cons.register_vote(i,'delete',old_vote=None)
            i.delete()

        vote = RatingVote.objects.filter(parent=cons)
        for r in vote:
            aso_rep_delete.send(sender=request.user, event_score=1, user=r.user,
                                initiator=request.user, dimension=ReputationDimension.objects.get('Vote'),
                                related_object=r,is_vote=True) # register reputation for voting
            user_cons.register_vote(r,'delete',old_vote=None)
            r.delete()
        cons.delete()
        update_ranks(request)
        #need to also delete comments...
        #need to initiate update of this object
        return HttpResponse(simplejson.dumps({'FAIL': False, 'message': 'deleted'}),
                        mimetype='application/json')


def flagvote(request):
    if not request.user.is_authenticated()  or not request.user.is_active:
        #needs to popup registration dialog instead
        return HttpResponse(simplejson.dumps({'FAIL': True}), #need a better non-auth error here, interferes with view
                                mimetype='application/json')

    if request.method == 'POST':
        vote = int(request.POST[u'vote'])
        pk = int(request.POST[u'pk'])
        flag_type = str(request.POST['flag_type'])
        user_pk = int(request.POST['user'])
        if request.user.pk != user_pk:
            return HttpResponse(simplejson.dumps({'FAIL': True}),
                                mimetype='application/json')
        user = User(pk=user_pk)
        flag = Flag.objects.get(object_pk=pk, flag_type=flag_type)
        uflag, created = UserFlag.objects.get_or_create(user=user, flag=flag)
        cons = Consensus.objects.get(object_pk=pk)
        count = 0
        v = bool(vote)
        votestr = ''
        if uflag.mode == v and not created:
            if v == True:
                flag.votes = flag.votes - 1
                count = flag.votes
                votestr = 'vote_up_flat'
            elif v == False:
                flag.counters = flag.counters - 1
                count = flag.counters
                votestr = 'vote_down_flat'
            flag.save()
            aso_rep_delete.send(sender=user, event_score=1, user=user, initiator=user, dimension=ReputationDimension.objects.get('Flag'),related_object=uflag) # delete reputation is flag removed
            uflag.delete() 
        elif created:
            uflag.mode = v
            if v == True:
                flag.votes = flag.votes + 1
                count = flag.votes
                votestr = 'vote_up_acti'
            elif v == False:
                flag.counters = flag.counters + 1
                count = flag.counters
                votestr = 'vote_down_acti'
            uflag.save()
            flag.save()
            check_badges(cons.content_object.user, Flag, pk)
            aso_rep_event.send(sender=user, event_score=1, user=flag.content_object.user, initiator=user, dimension=ReputationDimension.objects.get('Flag'),related_object=uflag) # register reputation for flag creation
        imgsrc = '/static/voteimgs/' + votestr + '.gif'
        results = {'FAIL':False, 'count':count, 'modes':str(vote == 0), 'imgsrc':imgsrc}
        if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            return HttpResponse(simplejson.dumps(results),
                                mimetype='application/json')

#sets location in REQUEST dict to access google maps API
def set_loc_by_ip(request):     
    request.session['city']  = str(request.POST[u'city'])
    request.session['region'] = str(request.POST[u'region'])
    request.session['country'] = str(request.POST[u'country'])
    return HttpResponse(simplejson.dumps({'FAIL':False}), #need a better non-auth error here, interferes with view
                                mimetype='application/json')

def add_tag(request):
    if not request.user.is_authenticated()  or not request.user.is_active:
        #needs to popup registration dialog instead
        return HttpResponse(simplejson.dumps({'FAIL':True}), #need a better non-auth error here, interferes with view
                                mimetype='application/json')

    if request.method == 'POST':
        obj_id = int(request.POST[u'obj'])
        tag = str(request.POST[u'tag'])
        c_type = str(request.POST['c_type'])
        app_type = str(request.POST['app_type'])
        
        model_type = ContentType.objects.get(app_label=app_type, model=c_type)
        obj = model_type.get_object_for_this_type(pk=obj_id)
        
        Tag.objects.add_tag(obj, tag)
        new_tag = Tag.objects.get(name=tag)
        
        try:relationship_event.send(sender=new_tag,obj=new_tag,parent=obj,initiator=request.user)
        except:pass
        results = {'linktaglist': get_link_tag_list(request.user,obj,get_links=True),'taglist':get_recommended_tag_list(obj, get_links=True),'FAIL':False}
        return HttpResponse(simplejson.dumps(results),
                    mimetype='application/json')
                    
                    
def del_tag(request):
    if not request.user.is_authenticated()  or not request.user.is_active:
        #needs to popup registration dialog instead
        return HttpResponse(simplejson.dumps({'FAIL':True}), #need a better non-auth error here, interferes with view
                                mimetype='application/json')

    if request.method == 'POST':
        obj_id = int(request.POST[u'obj'])
        tag = str(request.POST[u'tag'])
        c_type = str(request.POST['c_type'])
        app_type = str(request.POST['app_type'])
        
        model_type = ContentType.objects.get(app_label=app_type, model=c_type)
        obj = model_type.get_object_for_this_type(pk=obj_id)
        
        tagobj = Tag.objects.get(name=tag)
        taggedobj = TaggedItem.objects.get(tag_name=tag,object_id=obj.pk)
        delete_relationship_event.send(sender=tagobj,obj=tagobj,parent=obj,initiator=request.user)
        taggedobj.delete()
        results = {'linktaglist': get_link_tag_list(request.user,obj,get_links=True),'taglist':get_recommended_tag_list(obj,get_links=True),'FAIL':False}
        return HttpResponse(simplejson.dumps(results),
                    mimetype='application/json')
            
def starvote(request):
    '''
    This is the POST function that is the django part of the Ajax/Javascript 
    asynchronous voting function. The function receives a request from a 
    consensus object, and creates/deletes a UpDownVote object as requested from
    the Javascript that calls this function.
    
    Returns: JSON object containing an updated count to modify vote totals in UI,
    and a image filename to modify graphical elements of the UI.
    '''

    if not request.user.is_authenticated()  or not request.user.is_active:
        return HttpResponse(simplejson.dumps({'FAIL': True}),
                                mimetype='application/json')
                                
    if request.method == 'POST':
        
        pk = request.POST[u'pk']
        vote_str = int(request.POST[u'vote'])

        consensus = Consensus.objects.get(object_pk=pk)
        cnt = ContentType.objects.get_for_model(User)
        user_cons, is_new = Consensus.objects.get_or_create(content_type=cnt,
                                    object_pk=request.user.pk,
                                    parent_pk=request.user.pk,
                                    vote_type=cnt)
        if is_new:
            user_cons.intiate_vote_distributions()

        if vote_str == -99:
            st = RatingVote.objects.get(user=request.user, object_pk=pk)
            aso_rep_delete.send(sender=request.user, event_score=1, user=consensus.content_object.user, initiator=request.user, dimension=ReputationDimension.objects.get('Vote'),related_object=st,is_vote=True) # register reputation for voting
            user_cons.register_vote(st,'delete',old_vote=None)
            update_agent.send(sender=user_cons, type="vote", params=['objective', st.pk])
            st.delete()
        else:
            try: #TODO: there is an error happening here!
                old = RatingVote.objects.get(user=request.user, object_pk=pk)
                if old.vote_pos != vote_str:
                    old_vote_pos = old.vote_pos
                    old.vote_pos = vote_str
                    old.save()
                    user_cons.register_vote(old,'change',old_vote=old_vote_pos)
                    vote_created_callback(sender=request.user, parent=consensus,vote_type=vote_str)
                    
            except:
                st = RatingVote(user=request.user, parent=consensus, vote_pos=vote_str, object_pk=pk, parent_pk=consensus.parent_pk)
                st.save(),
                check_badges(consensus.content_object.user, RatingVote, pk)
                aso_rep_event.send(sender=request.user, event_score=1, user=consensus.content_object.user, initiator=request.user, dimension=ReputationDimension.objects.get('Vote'),related_object=st, is_vote=True) # register reputation for voting
                vote_created_callback(sender=request.user, parent=consensus,vote_type=vote_str)
                user_cons.register_vote(st,'register')
                update_agent.send(sender=user_cons, type="vote", params=['objective', st.pk])

        results = {'FAIL':False, 'vote_str':vote_str }
        if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            return HttpResponse(simplejson.dumps(results),
                                mimetype='application/json')

def vote(request):
    '''
    This is the POST function that is the django part of the Ajax/Javascript 
    asynchronous voting function. The function receives a request from a 
    consensus object, and creates/deletes a UpDownVote object as requested from
    the Javascript that calls this function.
    
    Returns: JSON object containing an updated count to modify vote totals in UI,
    and a image filename to modify graphical elements of the UI.
    '''

    vote_dict = {'up': 1,'down': -1,'neut': 0}
    if not request.user.is_authenticated()  or not request.user.is_active:
        #needs to popup registration dialog instead
        return HttpResponse(simplejson.dumps({'FAIL':True}), #need a better non-auth error here, interferes with view
                                mimetype='application/json')
                                
    if request.method == 'POST':
        c = None
        pk = int(request.POST[u'pk'])
        vote_str = request.POST[u'vote']
        img_size = request.POST[u'img_size']
        consensus = Consensus.objects.get(object_pk=pk)
        upd = UpDownVote.objects.filter(parent=consensus,user=request.user)
        newu = upd.count()
        vote_type = vote_dict[vote_str]
        if newu == 0: #if user has never voted on this consensus object, create new vote    
            new_vote = UpDownVote(vote_type=vote_type,parent=consensus,submit_date=datetime.datetime.now(),user=request.user)
            new_vote.save()
            #c = UpDownVote.objects.filter(vote_type=vote_type,parent=consensus).count()
            imgsrc = "/static/voteimgs/" + vote_str + "_arrow_acti" + img_size + ".png"
            #create reputation event for this vote_dict
        
            user = consensus.content_object.user
            aso_rep_event.send(sender=request.user, event_score=1, user=user, initiator=request.user, dimension=ReputationDimension.objects.get('Voting'),related_object=new_vote)
            vote_created_callback(sender=request.user, parent=consensus,vote_type=vote_type)
            
        else: #if this user has already voted
            vote_id = int(upd[0].vote_type)
            if vote_type == vote_id: #if user clicked on same vote, delete old vote
                user = consensus.content_object.user
                aso_rep_delete.send(sender=request.user, event_score=1, user=user, initiator=request.user, dimension=ReputationDimension.objects.get('Voting'),related_object=upd[0])
                upd[0].delete()
                #c = UpDownVote.objects.filter(vote_type=vote_id,parent=consensus).count()
            #else: #else do nothing.
                #c = UpDownVote.objects.filter(vote_type=vote_type,parent=consensus).count()
            imgsrc = "/static/voteimgs/" + vote_str  + "_arrow_flat" + img_size + ".png"
        results = {'count':str(c),'imgsrc':imgsrc,'FAIL':False }
        if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            return HttpResponse(simplejson.dumps(results),
                                mimetype='application/json')
                                


def spectrumvote(request):
    '''
    This is the POST function that is the django part of the Ajax/Javascript 
    asynchronous voting function. The function receives a request from a 
    consensus object, and creates/deletes a UpDownVote object as requested from
    the Javascript that calls this function.
    
    Returns: JSON object containing an updated count to modify vote totals in UI,
    and a image filename to modify graphical elements of the UI.
    '''

    if not request.user.is_authenticated()  or not request.user.is_active:
        #needs to popup registration dialog instead
        return HttpResponse(simplejson.dumps({'FAIL':True}), #need a better non-auth error here, interferes with view
                                mimetype='application/json')
                                
    if request.method == 'POST':
        
        pk = request.POST[u'pk']
        vote_str = int(request.POST[u'vote'])

        consensus = Consensus.objects.get(object_pk=pk)
        cnt = ContentType.objects.get_for_model(User)
        user_cons, is_new = Consensus.objects.get_or_create(content_type=cnt, 
                                    object_pk=request.user.pk,
                                    parent_pk=request.user.pk,
                                    vote_type=cnt)
        if is_new:
            user_cons.intiate_vote_distributions()
        if vote_str == -99:
            try:
                st = UpDownVote.objects.get(user=request.user, object_pk=pk)
                aso_rep_delete.send(sender=request.user, event_score=1, user=consensus.content_object.user, initiator=request.user, dimension=ReputationDimension.objects.get('Vote'),related_object=st, is_vote=True)
                user_cons.register_vote(st,'delete')
                update_agent.send(sender=user_cons, type="vote", params=['subjective', st.pk])
                st.delete()
            except:
                raise ValueError('Tried to cancel a vote that doesnt exist')
        else:
            try:
                old = UpDownVote.objects.get(user=request.user, object_pk=pk)
                if old.vote_type != vote_str:
                    old_vote_pos = old.vote_type
                    old.vote_type = vote_str
                    old.save()
                    user_cons.register_vote(old, 'change', old_vote=old_vote_pos)
                    vote_created_callback(sender=request.user, parent=consensus, vote_type=vote_str)

            except Exception, e:
                st = UpDownVote(user=request.user, parent=consensus, vote_type=vote_str, object_pk=pk, parent_pk=consensus.parent_pk)
                st.save()
                check_badges(consensus.content_object.user, UpDownVote, pk)
                aso_rep_event.send(sender=request.user, event_score=1, user=consensus.content_object.user, initiator=request.user, dimension=ReputationDimension.objects.get('Vote'),related_object=st, is_vote=True) # register reputation for voting
                vote_created_callback(sender=request.user, parent=consensus, vote_type=vote_str) 
                user_cons.register_vote(st, 'register')  
                update_agent.send(sender=user_cons, type="vote", params=['subjective', st.pk])
        results = {'FAIL': False, 'vote_str': vote_str}
        if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
            return HttpResponse(simplejson.dumps(results),
                                mimetype='application/json')


##########DEPRECATED!!!#############################
#populates database with voting content for testing. I know it's ugly as hell, but I had this in it's own file and was having some import issues, thought
#it best to just put it here until it is defunct and no longer needed. If anyone feels up for it, extracting this to a file wouldn't be difficult.
def generate_vote_content(request):
    data = ['Help secure our Boarder by ending Marijuana Prohibition. Cartels make 60% of there profit from Pot and are the single biggest threat to our Boarder. The only thing the Prohibition of Marijuana has done is made our enemies stronger from the BILLIONS in Pot profit that they use to fund even more harmful activities and crimes. Government has NO RIGHT to tell someone what they can and cant put into there bodies as long as it does not harm anyone else. Anyone with common sense knows Pot fits right into that category.', 'American is not the welfare state for Mexico. We need to adopt Mexicos immigration law. We have an infestation of illegals because they have no respect for our country and refuse to obey our laws. Immigration numbers must be limited to a level that can be assimilated. Anchor babies and chain migration must stop. The current laws need to be enforced.', 'All Americans shall maintain Habeas Corpus. They who can give up essential liberty to obtain a little temporary safety, deserve neither liberty nor safety. Benjamin Franklin', 'Build entire fence along southern border, add more Border agents, add more ICE agents, impose heavy fines on employers using illegals, have all employers use E Verify, increase raids on employers, deport all illegals in our jails immediately, no more anchor babies, one parent needs to be US citizen, Deport all illegals over a 5 year period, do not allow any muslims to enter USA.', 'Terrorists abroad are not as great a threat as leftists at home.', 'I think that the party should take the advice of great conservative Barry Goldwater and let gay serve openly in the Armed Forces, as he said You dont have to be straight to shoot straight', 'All US Citizens should know the US Constitution forwards & backwards. We need to ensure that it is being taught extensively to our children. Also, all Government Officials, Law Enforcement Officers & Military should be required to study it as they are required to swear an oath to uphold & protect it...kind of hard to do when you dont know or understand what it says.', 'The United States congress should only make laws that adhere to constitution. They should declare war when they go to war. They should protect our nation and only our nation. This includes closing down the more than 700 bases in over 150 countries. Bring the troops home, send them to border, and stop spending money to fund the military industrial complex. It is destroying our economy.', 'If youve served honorably for 4 years, you should full scholarship to any University in this country if you qualify to get in. The wonky post 9/11 GI Bill doesnt cut it. ALL vets should be covered fully.', 'Most military spending goes to expensive cold-war era hardware designed for nation-on-nation wars. This stuff doesnt make any sense in an era of guerilla war and terrorism. End these wasteful pork projects and redirect the money to our troops! They need better body armor, rifles, vehicles, and other equipment. We could save money AND have better train and equip our men in uniform. Boys before toys!', 'Follow the lead of Israel and require every high school graduate to qualify and serve in one of the military branches for 2 years. Once enlisted, everyone gets a chance at a college education to further their military career with the requirement that one year of college = one more year of enlistment. After their honorable discharge, they become a member of ther Reserves and are required to remain available for callback to their active branch of service until the age of 40. During this time they keep their military issue gear and weapons and are allowed to upgrade when replacements come up to the active service.', 'Abolish the IRS (70,320 pages and $304 billion a year compliance cost) which is nothing more than a greedy, institutionalized stealing agency. Its immoral and inhumane to steal peoples fruit of labor. End taxes at all levels of income for businesses and workers including payroll taxes. This will reduce the price of goods/services (govt induced inflation) and increase workers take home pay. Pass a law that govt can only tax at the point of consumption (no more than 15%) where it is clear, straight forward and visible to the consumer - no more hidden taxes built into the price like in gas, cigs, alcohol, etc. The poor and lower middles classes who use 90% of govt services yet pay zero federal income taxes would pay their fair share and the rich would no longer seek tax shelters to hide their money since making money and succeeding is no longer punished by the federal govt. One national sales tax is a much fairer tax system that doesnt allow politicians to divide people into income groups for political gain. Its none of the govts business how much a person makes.', 'Stop the outsourcing of jobs from America to other countries that do not pay taxes into the U.S. and stop the tax breaks that are given to these companies that are outsourcing. If there company is in the United States, hire people in the United States. That would create more revenue for the government as the American workers would pay taxes and the companies would be paying taxes to America as well.', 'ENACT THE FAIR TAX and end the IRS. Not a flat tax, not some future adjustable tax reform, but the Fair Tax is the way to boost our economy while ending Congress ability to re-distribute wealth or manipulate behavior the way they have with the income-based tax system. Other benefits: it will attract businesses to locate themselves in the USA (increasing jobs), it collects taxes from EVERYONE here (including tourists and illegal aliens), and most importantly taxes arent hidden in your payroll check, they are obvious every time you purchase something.', 'Balanced Budget, Eliminate Dept of Education, eliminate estate tax, cpa cap gain tax at 15%, Eliminate the IRS, institute a flat tax rate, reduce govt bureaucracy and spending, no more earmarks', 'Transparency - American taxpayers deserve to see where their tax dollars are going, on the way into the legislative process and on the way out. This means ending the practice of rushing bills through Congress at the speed of light by requiring legislation be posted online for five days before it can be scheduled for a floor vote. This gives taxpayers the opportunity to read bills and offer feedback and potentially devastating legislation. We also must demand that ALL government expenditures, down to the line-item expense, be put online in a searchable, easily accessible format so taxpayers can track, dollar-for-dollar, where their hard-earned money is going. The only way to stop the spending is to keep representatives accountable - American taxpayers deserve the tools that will empower them to become good fiscal watchdogs of the state.', 'Reduce the size of our military spending drastically. Its currently over 50% of our national budget and doesnt need to be so gargantuan. Our carrier fleet alone is several times larger than the entire worlds fleets put together. If you cut that by itself youd save the American taxpayer quite a bit of money and even have some left over for infrastructure improvements, better schools and social programs that will make this nation stronger over all.']
    topics = l=['taxes','congress','jobs','freedom','constitution','budget','spending','abortion','immigration','tax','accountability','economy ','government-reform ','national-security ','job ','obama ','education ','religion ','military ','reform ','welfare-reform ','health ','government ','waste ','corruption ','debt ','oil ','health-care ','unemployment ','energy ','illegal ','bp ','liberty ','immigration ','constituion ','terrorism ','marriage ','deficit ','voting ','security ','healthcare ','tax-reform ','regulation ','marijuana ','national ','unions ','medicare ','environment ','term ','immigration-dude ','citizenship ','values ','prosperity ','job-creation ','border-patrol','defense ','term-limits ','fiscal ','border-control ','tax ','Government ','life-health ','irs ','amendment ','social-security ','crime ','illegal-immigration ','Social ','schools ','social-secuirty ','drugs ','war ','law ','president ','epa ','senate ','immigratiion ','elections ','website-problems ','republicans ','taxation ','socialism ','immagration ','atr ','bills ','trade ','money ','liberty-and-freedom ','patriotism ','fiscal-accountability ','fiscal-responsibility ','budget ','welfare ','earmarks ','flat-tax ','god ','censorship','obamacare ','family-values','balanced']
    import random
    users = 10
    issues = 100
    votes = 1000
    ulist = []
    u_pref = []
    from django.contrib.auth.models import User 
    for i in range(users): #create 100 random users 
        f = User()
        f.save()
        ulist.append(f)
    tlist = {}
    from pirate_issues.models import Topic,Issue
    from pirate_consensus.models import Consensus
    for i in range(len(topics)):
        topic = Topic(text=topics[i])
        topic.save()
        tlist[topics[i]] = i
    u_pref = [[random.random() for j in range(len(topics))] for i in range(users)]
    u_mag = [[random.random() for j in range(len(topics))] for i in range(users)]
    #now we have users and topics set up, start creating issues
    issue_list = []
    for i in range(issues):
        n = 'Def'
        text = data[random.randint(0,len(data)-1)]
        topic = Topic.objects.get(text = tlist.keys()[random.randint(0,len(tlist.keys())-1)])
        iss = Issue(name=n, text=text, topic=topic)
        iss.save()
        issue_list.append(iss)
        contype = ContentType.objects.get_for_model(Issue)
        cons = Consensus(submit_date=datetime.datetime.now(),content_type=contype,content_object=iss,object_pk=iss.id)
        cons.save()
    #now the groups of users vote on the, roulette wheel over preferences
    for j in range(votes):
        idx = int(random.random()*(len(ulist)-1))
        u = ulist[idx]
        roulette = random.random() * sum(u_pref[idx])
        for k in issue_list:
            roulette -= u_pref[idx][tlist[k.topic.text]]
            if roulette <= 0:
                vt = k
                break
        val = u_mag[idx][tlist[vt.topic.text]]
        cons = Consensus.objects.get(object_pk = k.id)
        if val < .3:
            new_vote = UpDownVote(vote_type=-1,parent=cons,submit_date=datetime.datetime.now(),user=u)
            new_vote.save()
        elif val > .3 and val < .6:
            new_vote = UpDownVote(vote_type=0,parent=cons,submit_date=datetime.datetime.now(),user=u)
            new_vote.save()
        else:
            new_vote = UpDownVote(vote_type=1,parent=cons,submit_date=datetime.datetime.now(),user=u)
            new_vote.save()
        if j % 100 == 0: random.shuffle(issue_list)
        

        
def setup_admin(request):
    users = User.objects.filter(is_active=True, is_superuser=True).all()
    
    if len(users) == 0:
        user = User.objects.create_superuser("admin","piratepolitics@gmail.com","password")
        resp = "Superuser with name 'admin' and password 'password' created." 
        return HttpResponse(resp)
    
    elif len(users) > 0:
        number = len(users)
        first = users[0]
        resp = "%s superuser(s) already exist(s), including user with username '%s'" \
             % (number, first.username)
        return HttpResponse(resp)

    else:
        raise Exception("This should not be reached.")  
