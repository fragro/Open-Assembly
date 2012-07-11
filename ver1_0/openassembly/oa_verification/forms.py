from django import forms
from pirate_sources.models import IMGSource
from django import db
from pirate_core.widgets import HorizRadioRenderer
from django.contrib.auth.models import User


class arpvForm(forms.Form):
    #class Meta:
     #   model = arpv
      #  exclude = ('User1', 'User2', 'User1Confirm', 'User2Confirm', 'OtherConfirm')

    def save(self, commit=True):
        newo = super(arpvForm, self).save(commit=commit)
        return newo

    form_id = forms.CharField(widget=forms.HiddenInput(), initial="oa_arpv_form")
    user1 = forms.ModelChoiceField(label=(u'User1'), queryset=User.objects.all())
    user2 = forms.ModelChoiceField(label=(u'User2'), queryset=User.objects.all())
    photo = forms.ModelChoiceField(widget=forms.RadioSelect(renderer=HorizRadioRenderer),
                    queryset=IMGSource.objects.all())

    def _init_(self, curruser, *args, **kwargs):
        self.queryset = IMGSource.objects.filter(user=curruser)


class ReferralForm(forms.Form):

    def save(self, commit=True):
        newo = super(ReferralForm, self).save(commit=commit)
        return newo

    email = forms.CharField(label=(u'Email'), widget=forms.Textarea)
