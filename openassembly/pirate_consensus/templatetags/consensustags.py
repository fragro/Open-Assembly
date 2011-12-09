from django import template
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson

from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from pirate_core.views import HttpRedirectException, namespace_get
from pirate_consensus.models import  UpDownVote, Consensus,  RankedVote, WeightedVote, RatingVote, SpectrumHolder

from pirate_core.widgets import HorizRadioRenderer

from customtags.decorators import block_decorator
register = template.Library()
block = block_decorator(register)

RATINGS_CHOICES = (
    (1, "Empty of Value"),
    (2, "Poor"),
    (3, "OK"),
    (4, "Good"),
    (5, "Excellent"),
)

SPECTRUM_CHOICES = (
    (1, "Never!"),
    (2, "Strongly Disagree"),
    (3, "Disagree"),
    (4, "Mostly Disagree"),
    (5, "Pt. of Contention"),
    (6, "Meh"),
    (7, "Slightly Agree"),
    (8, "Mostly Agree"),
    (9, "Agree"),
    (10, "Strongly Agree"),
    (11, "Extremely Agree"),
)

SPECTRUM_COLORS = {
    1: "#e11010",
    2: "#e13310",
    3: "#e15610",
    4: "#e17810",
    5: "#e19b10",
    6: "#e1be10",
    7: "#e1e110",
    8: "#bee110",
    9: "#9be110",
    10: "#78e110",
    11: "#56e110",
}

get_namespace = namespace_get('pp_consensus')


@block
def pp_get_votes(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    user = kwargs.pop('user', None)
    obj = kwargs.pop('object', None)

    votes = UpDownVote.objects.filter(object_pk=obj.pk).filter(user=user).order_by('vote')

    namespace['votes'] = votes
    namespace['count'] = votes.count()
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_consensus_get(context, nodelist, *args, **kwargs):
    #retrieves a consensus object, places that object into the context.
    #Within this tag block an {include} should populate the html with a
    #consensus_widget that uses the context provided by this tag to create
    #the fields for voting and observing the consensus object.

    context.push()
    namespace = get_namespace(context)

    object_pk = kwargs.pop('object', None)

    if object_pk is None:
        raise ValueError("pp_consensus_get tag requires that a object id be passed "
                             "to it assigned to the 'object=' argument, and that the str "
                             "be assigned the string value 'consensus.")
    user = kwargs.pop('user', None)

    try:
        namespace['consensus'] = Consensus.objects.get(object_pk=object_pk)

        namespace['interest'] = namespace['consensus'].interest
        namespace['controversy'] = namespace['consensus'].controversy
        namespace['votes'] = namespace['consensus'].votes

        namespace['content_type'] = namespace['consensus'].content_type
        #user specific rendering of vote info
        #if available include it, else set to None
        try:
            updown = UpDownVote.objects.get(user=user, parent=namespace['consensus']).vote
        except:
            updown = None
        try:
            rate = RatingVote.objects.get(user=user, parent=namespace['consensus']).vote
        except:
            rate = None
        namespace['user_updown'] = updown
        namespace['user_rating'] = rate

    except:
        namespace['consensus'] = None
    output = nodelist.render(context)
    context.pop()

    return output

#Creates fields for creation of a consensus object, to be added to the object that is being referenced. This form includes settings for time constraints, if allowed at the global level. Some objects such as issues require a consensus object and therefore do not have a form attached.
@block
def pp_consensus_form(context, nodelist, *args, **kwargs): 
    """
    Populates the context with a ConsensusForm, allowing users to select what
    voting type is applied to the object or the objects children.
    
    Unless the number of related objects is limited, for example solutions to 
    a problem, plurality voting is required. As the number of objects considered
    for voting increases, it becomes increasingly impossible to rank or apply 
    weighted voting to the entire set.
    """
    context.push()
    namespace = get_namespace(context)

    obj = kwargs.pop('object', None)
    POST = kwargs.pop('POST', None)

    
    if POST is not None and POST.get("form_id") == "pp_consensus_form":

        form = ConsensusForm(POST)
        if form.is_valid():
            vote_type = form.cleaned_data['vote_type']
            if vote_type == "Ranked Voting":
                vt = ContentType.objects.get_for_model(RankedVote)
            elif vote_type == "Up/Down Voting":
                vt = ContentType.objects.get_for_model(UpDownVote)
            elif vote_type == "Weighted Voting":
                vt = ContentType.objects.get_for_model(WeightedVote)
            
            con = Consensus.objects.get(object_pk=obj.pk) 
            
            if obj.child != None:
                con.child_vote_type = vt
                con.save()
                
            namespace['complete'] = True
            namespace['vote_type'] = con.child_vote_type                                  
    else:
        form = ConsensusForm()
        con = Consensus.objects.get(object_pk=obj.pk)
        if con.child_vote_type != None:
            namespace['complete'] = True
            namespace['vote_type'] = con.child_vote_type
        else:
            namespace['complete'] = False
    namespace['form'] = form

        
    output = nodelist.render(context)
    context.pop()

    return output
    
@block
def pp_rating_form(context, nodelist, *args, **kwargs): 
    """
    Populates the context with a RatingForm, allowing users to select what
    voting type is applied to the object or the objects children.
    
    Unless the number of related objects is limited, for example solutions to 
    a problem, plurality voting is required. As the number of objects considered
    for voting increases, it becomes increasingly impossible to rank or apply 
    weighted voting to the entire set.
    """
    context.push()
    namespace = get_namespace(context)

    obj = kwargs.pop('object', None)
    POST = kwargs.pop('POST', None)
    user = kwargs.get('user', None)

    
    if POST is not None and POST.get("form_id") == "pp_rating_form":

        form = RatingForm(POST)
        if form.is_valid():
            rating = form.cleaned_data['rating']
            consensus = Consensus.objects.get(object_pk= obj.pk)
            st = RatingVote(user=user, parent=consensus, vote=rating)
    else:   
        try: 
            prev_rating = RatingVote.objects.get(user=user, object_pk=obj.pk)
            form = RatingForm(initial={'rating': prev_rating.vote})
        except: form = RatingForm()
        
    namespace['form'] = form

        
    output = nodelist.render(context)
    context.pop()

    return output

@block
def pp_spectrum_form(context, nodelist, *args, **kwargs): 
    """
    Populates the context with a SpectrumForm, allowing users to select what
    voting type is applied to the object or the objects children.
    
    Unless the number of related objects is limited, for example solutions to 
    a problem, plurality voting is required. As the number of objects considered
    for voting increases, it becomes increasingly impossible to rank or apply 
    weighted voting to the entire set.
    """
    context.push()
    namespace = get_namespace(context)

    obj = kwargs.pop('object', None)
    POST = kwargs.pop('POST', None)
    user = kwargs.get('user', None)
    dimenion = kwargs.get('dimension', None)

    
    if POST is not None and POST.get("form_id") == "pp_spectrum_form":

        form = SpectrumForm(POST)
        if form.is_valid():
            rating = form.cleaned_data['spectrum']
            consensus = Consensus.objects.get(object_pk=obj.pk)
            #st = RatingVote(user=user, parent=consensus, vote=rating)
    else:
        try:
            prev_rating = UpDownVote.objects.get(user=user, object_pk=obj.pk)
            form = SpectrumForm(initial={'spectrum': prev_rating.vote})
        except:
            form = SpectrumForm()
        
    namespace['form'] = form

        
    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_rating_js(context, nodelist, *args, **kwargs):
    
    context.push()
    namespace = get_namespace(context)
    
    obj = kwargs.get('object', None)
        
    if obj: 
        RET = """
        $(function(){
                $("#stars-wrapper-rate""" + str(obj.id) + """").stars({
	               inputType: "select",
	               callback: function(ui, type, value){
                        starvote(""" + "'" + str(obj.id) + "'" + """, value);
                   },
                   captionEl: $("#stars-cap-rate"),
                   cancelTitle:'Cancel Rating',
                   cancelValue:-99
                });
            });
        """
    else: RET = ""
    namespace['rating_js'] = RET
        
    output = nodelist.render(context)
    context.pop()

    return output

@block
def pp_spectrum_js(context, nodelist, *args, **kwargs):
    
    context.push()
    namespace = get_namespace(context)
    
    obj = kwargs.get('object',None)
        
    if obj: 
        RET = """
        $(function(){
                $("#stars-wrapper-spec""" + str(obj.id) + """").stars({
	               inputType: "select",
	               callback: function(ui, type, value){
                        spectrumvote(""" + "'" + str(obj.id) + "'" + """, value);
                   },
                   spectrum:true,
                   captionEl: $("#stars-cap-spec"),
                   cancelTitle:'Cancel Vote',
                   cancelValue:-99

                });
            });
        """
    else: RET = ""
    namespace['spectrum_js'] = RET

    output = nodelist.render(context)
    context.pop()

    return output


@block
def pp_consensus_chart(context, nodelist, *args, **kwargs):

    context.push()
    namespace = get_namespace(context)

    obj = kwargs.get('object', None)
    #prepare data for highchart
    if obj.spectrum is not None:
        dchart = {'type': 'pie', 'name': 'Temperature Check'}
        data = []
        for i in SpectrumHolder.objects.filter(spectrum_pk=obj.spectrum.pk):
            data.append({'name': str(int(i.vote) - 6), 'y': i.value, 'color': SPECTRUM_COLORS[int(i.vote)]})
        dchart['data'] = data
        namespace['chart_data'] = str([dchart])
        namespace['chart'] = True
    output = nodelist.render(context)
    context.pop()

    return output


#: render a <link> tag required to be added to the template at the appropriate locations.
@block
def pp_consensus_css(context, nodelist, *args, **kwargs):
    pass

# pre-fetches all of the user votes that might be referenced by tags on the page, and stores them in the context, as a performance hack, so that the rendering of each widget does not cause a separate query to the data store. This is optional.
@block
def pp_consensus_user_block(context, nodelist, *args, **kwargs):
    pass

@block
def pp_consensus_info(context, nodelist, *args, **kwargs):
    pass 


VOTE_TYPES = (('Ranked Voting', 'Ranked Voting'), ('Weighted Voting','Weighted Voting'), ('Up/Down Voting','Up/Down Voting'))

#This shouldn't really be used in practice, consensus objects are generally automatically generated
class ConsensusForm(forms.Form):
    '''
    This form is used to allow creation and modification of consensus objects.  The form_id
    field is hidden and static and is used to allow the pp_consensus_form tag to identify 
    whether the POST included with the submission pertains to issues or does not.

    By convention, the value of this hidden field should be the same as the tag that
    will process the form.
    '''
        
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_consensus_form")
    vote_type = forms.ChoiceField(widget=forms.RadioSelect(renderer=HorizRadioRenderer),
                                        choices=VOTE_TYPES, required=True,
                                        label="Vote Type",initial="")    
                                        
class RatingForm(forms.Form):
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_rating_form")
    rating = forms.ChoiceField(choices=RATINGS_CHOICES)
    
class SpectrumForm(forms.Form):
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_spectrum_form")
    spectrum = forms.ChoiceField(choices=SPECTRUM_CHOICES)
