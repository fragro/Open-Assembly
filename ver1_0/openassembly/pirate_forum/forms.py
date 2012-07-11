from django import forms
import datetime

from django.contrib.contenttypes.models import ContentType
from pirate_forum.models import Question, Nomination

from pirate_core.fields import JqSplitDateTimeField
from pirate_core.widgets import JqSplitDateTimeWidget

from markitup.widgets import MarkItUpWidget


class BlobForm(forms.ModelForm):

    def save(self, commit=True):
        newo = super(BlobForm, self).save(commit=commit)
        if newo.created_dt == None:
            newo.created_dt = datetime.datetime.now()
            ctype = ContentType.objects.get_for_model(Nomination)
            newo.child = ctype
            newo.children = 0
        newo.modified_dt = datetime.datetime.now()
        return newo

    class Meta:
        model = Question
        exclude = ('parent', 'parent_pk', 'parent_type',
            'user', 'child', 'children', 'permission_req',
            'created_dt', 'modified_dt', 'forumdimension')

    summary = forms.CharField(max_length=100,
              widget=forms.TextInput(
                attrs={'size': '50', 'class': 'inputText'}), initial="")
    description = forms.CharField(widget=MarkItUpWidget(
                attrs={'cols': '20', 'rows': '10'}), initial="")

    long_term = forms.BooleanField(help_text="If this decision doesn't require a time for decision, ignore the following dates and times")
    end_of_nomination_phase = JqSplitDateTimeField(widget=JqSplitDateTimeWidget(attrs={'date_class': 'datepicker', 'time_class': 'timepicker'}))
    decision_time = JqSplitDateTimeField(widget=JqSplitDateTimeWidget(attrs={'date_class': 'datepicker', 'time_class': 'timepicker'}))
    winners = forms.IntegerField(help_text="Number of responses to accept, leave this blank to accept all responses.")
