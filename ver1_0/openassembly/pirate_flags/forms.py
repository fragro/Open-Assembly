from django import forms

FLAG_CHOICES = (
    ('Ad Hominem','Ad Hominem'),
    ('Straw Man','Straw Man'),
    ('False Dilemma','False Dilemma'),
    ('Appeal to Authority','Appeal to Authority'),
    ('Bandwagon','Bandwagon'),
    ('Cherry Picking','Cherry Picking'),
    ('Slippery Slope','Slippery Slope'),
    ('Red Herring','Red Herring')
)

class FlagForm(forms.Form):
    form_id = forms.CharField(widget=forms.HiddenInput(), initial="pp_flag_form")
    flag = forms.ChoiceField(choices=FLAG_CHOICES)
