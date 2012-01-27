from pirate_forum.models import ForumDimension, DimensionTracker
from pirate_topics.models import Topic
from pirate_consensus.models import Consensus, PhaseLink, Phase
from pirate_reputation.models import ReputationEvent
from django.contrib.contenttypes.models import ContentType
from pirate_consensus.models import RatingVote, UpDownVote
import datetime


#ForumDimension.objects.register(key='pro', name='Problem',
#	help_text ='Got a problem in the community? Describe your problem and seek the expertise of others.',
#	app_label = 'pirate_issues', model_class_name='Problem', form_class_name='ProblemForm')

#ForumDimension.objects.register(key='sol', name='Solution', help_text='Create a new solution for this problem.',
#								app_label='pirate_issues' , model_class_name= 'Solution', form_class_name='SolutionForm', is_child=True)

#ForumDimension.objects.register(key='pol', name='Policy', help_text="Policy statements are concise descriptions of some political stance, much like the planks of a modern political party's platform.",
#								app_label='pirate_issues', model_class_name='Policy' , form_class_name='PolicyForm')

#ForumDimension.objects.register(key='yea', name="Yea Argument", help_text="Argue for their claims!", app_label='pirate_deliberation',
#								 model_class_name='Argument', form_class_name='YeaArgumentForm', is_child=True)

#ForumDimension.objects.register(key='nay', name="Nay Argument", help_text="Argue against their claims!", app_label='pirate_deliberation',
#								 model_class_name='Argument', form_class_name='NayArgumentForm', is_child=True)

#ForumDimension.objects.register(key='mes', name='Message', help_text='', app_label='pirate_messages',
#								model_class_name='Message', form_class_name='MessageForm',is_content=False)

#ForumDimension.objects.register(key='fil', name='Film', help_text= 'Upload Film for Genome Project', 
#								app_label='oa_filmgenome', model_class_name='Film', form_class_name='FilmForm', is_admin=True)

#ForumDimension.objects.register(key='sce', name='Scene', help_text='Upload Scene for Genome Project',
#								app_label='oa_filmgenome', model_class_name='Scene', form_class_name='SceneForm', is_admin=True)

#ForumDimension.objects.register(key='bug', name='Bug', help_text='File a bug report and help improve Open Assembly',#
#								app_label='oa_suggest', model_class_name='Bug', form_class_name='BugForm',)

#ForumDimension.objects.register(key='sug', name='Suggestion', help_text='Got an idea for a feature? Let us know.',
#								app_label='oa_suggest' , model_class_name='Suggestion' , form_class_name='SuggestionForm',)

#ForumDimension.objects.register(key='eve', name= "Event", help_text='Create a new political action.',
#								app_label='pirate_actions', model_class_name='Action', form_class_name='ActionForm')

#ForumDimension.objects.register(key='act', name= "Action", help_text='Upload an event or create your own.',
#								app_label='pirate_actions', model_class_name='Event', form_class_name='EventForm')

#ForumDimension.objects.register(key='boy', name= "Boycott", help_text='Boycotts are an excellent way to fight the corporate abuse of power. Please include reasoning for boycott and the target.',
#								app_label='pirate_actions', model_class_name='Boycott', form_class_name='BoycottForm')


ForumDimension.objects.register(key='nom', name="Response", help_text='Respond to a Proposal',
								app_label='pirate_forum', model_class_name='Nomination', form_class_name='NominationForm', is_child=True)

ForumDimension.objects.register(key='pol', name="Proposal", help_text='Single Policy with Timed Decision. Nominate your ideas for policy or action and then vote on those. Optionally you can also rank the resulting ideas.',
								app_label='pirate_forum', model_class_name='Question', form_class_name='BlobForm')

ForumDimension.objects.register(key='tem', name="Temp. Check", help_text='Temperature Check of idea over time, no set time for decision',
								app_label='pirate_forum', model_class_name='Question', form_class_name='BlobForm')


#######GET OR CREATE OA_CACHE

def main():
	for r in RatingVote.objects.all():
		try:
			str(r)
			cons = r.parent
			r.parent_pk = cons.parent_pk
			r.save()
		except:
			r.delete()
	for r in UpDownVote.objects.all():
		try:
			str(r)
			cons = r.parent
			r.parent_pk = cons.parent_pk
			r.save()
		except:
			r.delete()
#	for i in ReputationEvent.objects.all():
#		consensus = i.related_object
#		try:
#			print str(consensus)
#		except:
#			i.delete()
	for exist in DimensionTracker.objects.all():
		exist.delete()
	for topic in Topic.objects.all():
		for fd in ForumDimension.objects.all():
			#issue_list = Consensus.objects.all()
			#issue_list = issue_list.filter(parent_pk=topic.pk)
			#type_class = ContentType.objects.get(app_label=str(fd.app_label), model=str(fd.model_class_name).lower())
			#issue_list = issue_list.filter(content_type=type_class)
			d, is_new = DimensionTracker.objects.get_or_create(object_pk=topic.pk,dimension=fd)
			#d.children = issue_list.count()
			d.save()


### CREATE THE PHASELINKS and LINKS BETWEEN THEM

ph1, is_new = PhaseLink.objects.get_or_create(phasename="nom", verb="pose your question")
ph2, is_new = PhaseLink.objects.get_or_create(phasename="vote", verb="nominate a solution and debate")
ph3, is_new = PhaseLink.objects.get_or_create(phasename="decision", verb="vote to make a decision")


ph1.prevphase = None
ph1.nextphase = ph2
ph1.save()

ph2.prevphase = ph1
ph2.nextphase = ph3
ph2.save()

ph3.prevphase = ph2
ph3.nextphase = None
ph3.save()

#Fix all the existing consensus objects
###DANGEROUS OPERATION, SHOULD ONLY BE DONE ONCE

#for cons in Consensus.objects.all():
#	ph = Phase(consensus=cons, curphase=ph3,
#				creation_dt=datetime.datetime.now(), decision_dt=datetime.datetime.now(),
#				phase_change_dt=datetime.datetime.now(), complete=True, active=True)
#	ph.save()
#	cons.phase = ph
#	cons.save()

main()
