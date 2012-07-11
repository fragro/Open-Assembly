# Create your views here.
from django.http import HttpResponse
import simplejson
import datetime
from pirate_consensus.models import ConfirmRankedVote, RankedVote, Consensus


def set_ranked_vote(request):
    if not request.user.is_authenticated() or not request.user.is_active:
        return HttpResponse(simplejson.dumps({'FAIL': True}),
                                mimetype='application/json')

    if request.method == 'POST':
        rl = request.POST[u'ranked_list']
        object_pk = request.POST[u'object_pk']

        cons = Consensus.objects.get(pk=object_pk)

        rl = rl.split(',')

        rank = 1
        rl_ret = []
        for cons_id in rl:
            if cons_id != '':
                rl_ret.append(cons_id)
                nom = Consensus.objects.get(pk=cons_id)
                try:
                    rvote = RankedVote.objects.get(parent=cons, nom_cons=nom, user=request.user)
                except:
                    rvote = RankedVote(parent=cons, nom_cons=nom, user=request.user)
                rvote.ranked_vote = rank
                rank += 1
                rvote.save()

        #rvote.ranked_list = rl.split(',')
        #rvote.save()
        results = {'FAIL': False, 'rvote': rl_ret, 'now': 'Ranking Updated: ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    else:
        results = {'FAIL': True}
    if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
        return HttpResponse(simplejson.dumps(results),
                            mimetype='application/json')


def confirm_ranked_vote(request):
    if not request.user.is_authenticated() or not request.user.is_active:
        return HttpResponse(simplejson.dumps({'FAIL': True}),
                                mimetype='application/json')

    if request.method == 'POST':
        object_pk = request.POST[u'object_pk']

        cons = Consensus.objects.get(pk=object_pk)
        try:
            rvote = ConfirmRankedVote.objects.get(parent=cons,
                user=request.user, submit_date=datetime.datetime.now())
            rvote.confirm = True
        except:
            rvote = ConfirmRankedVote(parent=cons,
                user=request.user, confirm=True, submit_date=datetime.datetime.now())
        rvote.save()
        js = "ranked_vote_confirm('" + object_pk + "',false);"
        text = """<span id="confirm_button"><a class="red btn_gen" style="margin-left:20px;" onClick=" """ + js + """ ">Delete Your Ranking</a>"""
        #rvote.ranked_list = rl.split(',')
        #rvote.save()
        results = {'FAIL': False, 'confirm_button': text}
    else:
        results = {'FAIL': True}
    if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
        return HttpResponse(simplejson.dumps(results),
                            mimetype='application/json')


def del_confirm_ranked_vote(request):
    if not request.user.is_authenticated() or not request.user.is_active:
        return HttpResponse(simplejson.dumps({'FAIL': True}),
                                mimetype='application/json')

    if request.method == 'POST':
        object_pk = request.POST[u'object_pk']

        cons = Consensus.objects.get(pk=object_pk)

        rvote = ConfirmRankedVote.objects.get(parent=cons,
                user=request.user)
        rvote.confirm = False

        js = "ranked_vote_confirm('" + object_pk + "',true);"
        text = """<span id="confirm_button"><a class="green btn_gen" style="margin-left:20px;" onClick=" """ + js + """ ">Confirm Your Ranking</a>"""

        #rvote.ranked_list = rl.split(',')
        #rvote.save()
        results = {'FAIL': False, 'confirm_button': text}
    else:
        results = {'FAIL': True}
    if 'application/json' in request.META.get('HTTP_ACCEPT', ''):
        return HttpResponse(simplejson.dumps(results),
                            mimetype='application/json')
