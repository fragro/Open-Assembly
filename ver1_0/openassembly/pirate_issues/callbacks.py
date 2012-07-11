from pirate_signals.models import aso_rep_event
from pirate_reputation.models import ReputationDimension

#Updates the issue.comments for each comment being posted
def update_issue_comment_count(sender, comment, request, **kwargs):
    aso_rep_event.send(sender = sender,event_score=1, user=comment.user, dimension=ReputationDimension.objects.get('add_comment'))
    
