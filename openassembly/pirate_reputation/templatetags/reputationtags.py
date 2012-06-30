from django import template
from django import forms
from django.http import HttpResponseRedirect
import datetime,sys
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from tagging.models import Tag, TaggedItem
from pirate_reputation.models import ReputationManager, Reputation, ReputationDimension, ReputationEvent, AbuseTicket
from pirate_consensus.models import Consensus
from pirate_forum.models import get_rangelist
from pirate_core import HttpRedirectException, namespace_get, FormMixin

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

get_namespace = namespace_get('pp_reputation')


@block
def pp_get_reputation_events_graph(context, nodelist, *args, **kwargs):
    '''
    This block tag can create or process forms to get tags.
    Usage is as follows:

    {% pp_get_reputation_events_graph user=request.object x=8 y=100 %}
       Do stuff with {{ pp_reputation.graph_html }}
    {% endpp_get_reputation %}

    This template tag dynamically generates the html required for a (x,y) graph
    where x is the activity rate and y is the time dimension. This graph shows
    users a basic idea of the user's activity rate.
    '''

    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    x = kwargs.get('x', None)
    y = kwargs.get('y', None)
    #must be divisible equally by days
    min_days = kwargs.get('min_days', None)
    #must be divisible equally by days
    graph_type = kwargs.get('type', None)

    if graph_type == None:
        raise ValueError("pp_get_reputation_events_graph requires type argument of 'rating','spectrum', or 'activity'")
    elif graph_type == 'activity':
        today = datetime.datetime.now()
        DD = datetime.timedelta(days=x)
        earlier = today - DD
        reps = ReputationEvent.objects.filter(initiator=user).order_by('-created_dt').filter(created_dt__gte=earlier)
        try:
            daylength = (reps[0].created_dt - reps[len(reps) - 1].created_dt).days + 2
        except:
            daylength = 1
        days = min(x, daylength)

        #if days == 2:
        #    days = 1 #side case for first day activity
        #    x=24
        #    min_days = 1
        #elif days > min_days:
        #    days = min_days
        #    x = 1
        #else: x = x * days
        html, rate_list, mtrx, min_rate, max_rate, mean = grab_graph(reps, x, y, days, min_days)
        namespace['days'] = daylength
    elif graph_type == 'spectrum' or 'rating':
        rate_list, min_rate, max_rate, mean = dist_graph(x, y, user, graph_type)

    namespace['x'] = x
    namespace['rate_list'] = rate_list
    namespace['min'] = min_rate
    namespace['max'] = max_rate
    namespace['mean'] = int(round(mean))

    output = nodelist.render(context)
    context.pop()
    return output


@block
def pp_get_reputation_events(context, nodelist, *args, **kwargs):
    '''
    This block tag can create or process forms to get tags.
    Usage is as follows:

    {% pp_get_reputation_events user=request.object %}
       Do stuff with {{ pp_reputation.reputation_events }}.
    {% endpp_get_reputation %}

    '''

    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    start = kwargs.get('start', 0)
    end = kwargs.get('end', 10)

    if user is not None and isinstance(user, User):
        #get argument score
        rep = ReputationEvent.objects.filter(initiator=user).order_by('-created_dt')
        cnt = rep.count()
    else:
        rep = []
        cnt = 0

    namespace['count'] = cnt
    namespace['reputation_events'] = rep[start:end]

    namespace['rangelist'] = get_rangelist(start, end, namespace['count'])

    output = nodelist.render(context)
    context.pop()
    return output


class ReportAbuseForm(forms.ModelForm):

    def save(self, commit=True):
        new_prof = super(ReportAbuseForm, self).save(commit=commit)
        return new_prof

    class Meta:
        model = AbuseTicket

        exclude = ('user', 'created_dt', 'fixed')

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="report_abuse")


@block
def abuse_ticket_form(context, nodelist, *args, **kwargs):
    '''
    This block tag can create or process forms either to create or to modify arguments.
    Usage is as follows:

    {% pp_profile_form POST=request.POST object=request.object %}
       Do stuff with {{ pp_profile.form }}.
    {% endpp_profile_form %}
    '''

    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)
    POST = kwargs.get('POST', None)

    if POST and POST.get("form_id") == "report_abuse":
            form = ReportAbuseForm(POST)
            #new_arg = form.save(commit=False)
            if form.is_valid():
                report_abuse_new = form.save(commit=False)
                report_abuse_new.user = user
                report_abuse_new.save()
                namespace['complete'] = True
            else:
                namespace['errors'] = form.errors
    else:
            form = ReportAbuseForm()

    namespace['form'] = form
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_get_reputation(context, nodelist, *args, **kwargs):
    '''
    This block tag can create or process forms to get tags.
    Usage is as follows:

    {% pp_get_reputation user=request.object %}
       Do stuff with {{ pp_reputation.reputation }}.
    {% endpp_get_reputation %}

    '''

    context.push()
    namespace = get_namespace(context)

    user = kwargs.get('user', None)

    if user is not None and isinstance(user, User):
        #get argument score
        scores = {}
        tot_score = 0
        for dim in ReputationDimension.objects.all():
            rep = Reputation.objects.get_user_score(user, dim)
            try:
                scores[str(dim)] = rep.score
                tot_score += rep.score
            except:
                pass
                #rep does not yet exist
    else:
        scores = {}
        tot_score = 0

    namespace['reputation_keys'] = scores.items()
    namespace['reputation'] = tot_score

    output = nodelist.render(context)
    context.pop()
    return output


#returns a graph of the distribution of votes for this user, based on dtype
#argument which is equal to 'spectrum' or 'rating' based on the opinion/quality
def dist_graph(x,y,user,dtype):
    rate_list, max_rate, min_rate, mean = distribution_graph(x,user,dtype=dtype)
    #mtrx = build_graph(rate_list, max_rate, y)
    #num = x/11
    #px = '1px'
    #dayslots=1;mcheck=True
    #html = generate_graph_html(x,y,dayslots,mtrx,mcheck,True,'1px',dtype)
    return rate_list, min_rate, max_rate, mean


#grabs an activity graph for the list of reputation events
def grab_graph(reps, x, y, days, min_days):
    dayslots = max(min(x/days,24),1) #must be at least one slot per day or less than equal to 24
    padding = min(0,x - (days*24))
    #iterate through rates and build matrix of boolean values
    if len(reps) != 0: 
        if days < x: rate_list, max_rate, min_rate, mean = activity_graph_greater(reps, x, y, days, dayslots)
        else: rate_list, max_rate, min_rate, mean = activity_graph_greater(reps, x, y, days, dayslots)
        mtrx = build_graph(rate_list, max_rate, y)
        mtrx = [[0 for i in range(y)] for j in range(padding)] + mtrx
        mcheck = True
        
    else: #there are no reputation events as of yet
        rate_list = []
        mtrx = [i for i in range(x)]
        min_rate = 0
        max_rate = 0
        mean = 0
        #generate html
        mcheck = False

    html = generate_graph_html(x,y,dayslots,mtrx,mcheck,False,'1px', None)

    return html, rate_list, mtrx, min_rate, max_rate, mean

#generates dynamic html using pixels to create a graph
"""
x: x length
y: y lenght
dayslots: pixels per day
mcheck: if we need to check the matrix, False for empty graphs
numcheck: if x vector determines pixel color, i.e. activity versus opinion graph
"""
def generate_graph_html(x,y,dayslots,mtrx,mcheck, numcheck, px, dtype):
    if dtype == 'spectrum': num = x/11
    elif dtype == 'rating': num = x/5
    html = "<div class='master_graph'><div class='graph'>"
    for i in range(len(mtrx)+2):html+='<img style="border:0;margin:' + px + ';" src="/static/border_pixel.gif">'
    html+='</div>'
    for i in range(y):
        html += "<div class='graph'>" +'<img style="border:0;margin:' + px + ';" src="/static/border_pixel.gif">'
        for j in range(len(mtrx)):
            if mcheck:
                if mtrx[j][i] == 1:
                    if numcheck:
                        html += '<img style="border:0;margin:'+px+';" src="/static/pixel_' + str((j/num)) + '.gif">'
                    else: html += '<img style="border:0;margin:' + px + ';" src="/static/pixel_0.gif">'
                else: html += '<img style="border:0;margin:' + px + ';" src="/static/trans_pixel.gif">'
            else: html += '<img style="border:0;margin:' + px + ';" src="/static/trans_pixel.gif">'
            
        html += '<img style="border:0;margin:' + px + ';" src="/static/border_pixel.gif">'+ "</div>"
    html += "<div class='graph'>"
    for i in range(len(mtrx)+2):html+='<img style="border:0;margin:' + px + ';" src="/static/border_pixel.gif">'
    html+='</div></div>'
    return html

def build_graph(rate_list, max_rate, y):
    #iterate through matrix and build html/css graph
    mtrx = []
    for rate in rate_list:
        try: rt = float(rate)/max_rate * y
        except: rt = 0
        col = [] 
        for j in range(y):
            if rt > j: col.append(1)
            else: col.append(0)
        col.reverse()
        mtrx.append(col)
    return mtrx

#shows distribution of votes on this user
def distribution_graph(x,user,dtype='spectrum'):
    contype = ContentType.objects.get_for_model(user)
    cons, is_new = Consensus.objects.get_or_create(content_type=contype, 
                                    object_pk=user.pk,
                                    vote_type= contype,
                                    parent_pk=user.pk)
    if is_new: cons.intiate_vote_distributions()
    if dtype == 'spectrum':
        l = cons.spectrum.get_list()
        idx = 1
    elif dtype == 'rating':
        l = cons.rating.get_list()
        idx = 2
    m_ax = 0
    ret_list = []
    num = x/len(l)
    m_in = sys.maxint
    tot = 0
    for spec in l:
        if spec[idx] > m_ax:
            m_ax = spec[idx]
        if spec[idx] < m_in:
            m_in = spec[idx]
        tot+=spec[idx]
        ret_list.extend([spec[idx] for i in range(num)])
    mean = float(tot)/len(l)
    return ret_list, m_ax, m_in, mean
        
# activity graph designed when length of time is greater than x and we 
#must only take a chunk of the events    
def activity_graph_greater(reps,x,y,days,dayslots):
    today = datetime.datetime.now()
    DD = datetime.timedelta(days=x)
    rate_list = []
    earlier = today - DD 
    itr = 0 
    min_rate = sys.maxint
    max_rate = 0
    rate = 0
    currep = reps[itr]
    for i in range(x,0,-1):
        while currep.created_dt.day == (earlier + datetime.timedelta(days=i)).day and currep.created_dt.month == (earlier + datetime.timedelta(days=i)).month:
            itr+=1 # next rep event 
            rate+=1
            try: currep = reps[itr]
            except: break
        rate_list.append(rate)
        if rate > max_rate: max_rate = rate 
        if rate < min_rate: min_rate = rate 
        rate = 0
    mean = sum(rate_list)/float(len(rate_list))
    rate_list.reverse()
    return rate_list, max_rate, min_rate, mean   
    
    
#returns graph from past activity, when less than x
def activity_graph(reps,x,y,days,dayslots):
    tday = reps[0].created_dt.day
    rate = 0
    min_rate = sys.maxint
    max_rate = 0
    num_days = 0
    rate_list = []
    tot_rate = 0.0
    range_list = []
    r = 0
    for i in range(dayslots):
        range_list.append((r,r+24/dayslots))
        r = r + 24/dayslots
    slots_list = [0 for i in range_list]
    for rep in reps: #iterate through each reputation event and segment into days and slots per day
        tot_rate+=1
        tmp_idx = 0
        if rep.created_dt.day == tday:
            for i in range_list: #check which slot in the day this event belongs to, iterate
                if rep.created_dt.hour in range(i[0],i[1]):
                    slot_idx = tmp_idx
                tmp_idx+=1
            try:slots_list[slot_idx] += 1
            except:pass #no data yet
        if rep.created_dt.day != tday:
            for rate in slots_list:
                if rate < min_rate: #check min rate
                    min_rate = rate
            for rate in slots_list:
                if rate > max_rate: #check max rate
                    max_rate = rate
            if tday < rep.created_dt.day: diff = (tday - rep.created_dt.day) * len(range_list[0])
            else: diff = len(range_list[0])
            rate_list = slots_list + rate_list
            for i in range(diff-1):
                 rate_list = [0 for i in range(dayslots)] + rate_list
            tday = rep.created_dt.day
            num_days+=diff
            slots_list = [0 for i in range_list]
            for i in range_list: #check which slot in the day this event belongs to, iterate
                if rep.created_dt.hour in range(i[0],i[1]):
                    slot_idx = tmp_idx
                tmp_idx+=1
            slots_list[slot_idx] += 1
    for rate in slots_list:
        if rate < min_rate: #check min rate
           min_rate = rate
    for rate in slots_list:
        if rate > max_rate: #check max rate
            max_rate = rate
    if tday < rep.created_dt.day: diff = (tday - rep.created_dt.day) * len(range_list[0])  
    else: diff = len(range_list[0])
    rate_list = slots_list + rate_list
    for i in range(diff-1):
        rate_list = [0 for i in range(dayslots)] + rate_list
    tday = rep.created_dt.day
    num_days+=diff
    mean = tot_rate/days
    
    return rate_list, max_rate, min_rate, mean
