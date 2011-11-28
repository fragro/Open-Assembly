from django import forms
from pirate_core.forms import FormMixin
from pirate_core.widgets import HorizRadioRenderer
from pirate_topics.models import Topic

class TopicForm(forms.Form, FormMixin):
    
    def save(self, commit=True):
        return None

    parent = forms.ModelChoiceField(queryset=Topic.clean_objects.all(),
                                        label="Group")
