from django import forms
from pirate_core.widgets import HorizRadioRenderer
from pirate_consensus.templatetags.consensustags import RATINGS_CHOICES, SPECTRUM_CHOICES, VOTE_TYPES

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
    spectrum = forms.ChoiceField(choices=SPECTRUM_CHOICES.items())
