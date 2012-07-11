import hashlib

from django.utils.translation import ugettext_lazy as _

from exceptions import ValueError, TypeError
from django import forms
from django.utils.datastructures import SortedDict

from pirate_core import HttpRedirectException


class FormMixin(object):

    @classmethod
    def create(self, POST=None, path=None, instance=None):

        if not issubclass(self, forms.BaseForm):
            raise TypeError("pirate_core.FormMixin should be used in multiple inheritance "
                            "in combination with a django.forms.BaseForm or subclass thereof.")

        Form = type(self.__name__, (self,), {})
        form_id = self.form_id(instance)
        Form.base_fields["form_id"] = self.form_id_field(form_id)

        if POST is not None:

            if not self.post_has_id(POST, form_id):
                form = Form() if instance is None else Form(instance=instance)
            else:
                form = Form(POST) if instance is None else Form(POST, instance=instance)

                if form.is_valid():
                    commit = False if path is None else True
                    form.save(commit=commit)
                    if path is not None:
                        e = HttpRedirectException(path)
                        e.form = form
                        raise e
        else:
            form = Form() if instance is None else Form(instance=instance)

        return form

    @classmethod
    def form_id(self, instance=None):
        if instance is None:
            instance_id = ""
        else:
            instance_id = "__" + instance.__module__ + "__" + instance.__class__.__name__
            if hasattr(instance, "pk"):
                instance_id += "__" + str(instance.pk)

        id_str = self.__module__.split(".")[-1] + "." + self.__name__ + instance_id
        return 'F' + hashlib.md5(id_str).hexdigest()

    @classmethod
    def form_id_field(self, form_id):
        return forms.CharField(widget=forms.HiddenInput(), required=False, initial=form_id)

    @classmethod
    def post_has_id(self, POST, form_id=None, instance=None):
        if form_id is None:
            form_id = self.form_id(instance)

        for key in POST:
            if "form_id" in key:
                if POST[key] == form_id:
                    return True
        return False


class ComboFormFactory(object):

    def __init__(self, *args):
        self._fields = SortedDict()
        self._forms = []
        self._fields['_forms'] = self._forms
        self._initial = {}
        self._fields['_initial'] = self._initial
        self._form_ids = []
        self._fields['_form_ids'] = self._form_ids
        base_fields = SortedDict()
        self._fields['base_fields'] = base_fields

        for form in args:
            if not isinstance(form, forms.BaseForm):
                raise ValueError("All arguments to the ComboForm constructor must be forms.")
            elif not hasattr(form, 'save'):
                raise ValueError("Only forms that implement a 'save' method can be added "
                                 "to the ComboForm.")

            self._forms.append(form)
            self._add_fields_for_form(form, base_fields)
        self._generate_class()
        self._render(base_fields)

    def _render(self, base_fields):
        for name, field in base_fields.items():
            base_fields[name].rendered = field.widget.render(name, self._initial[name], {'id': hashlib.md5(name).hexdigest()})

    def _add_fields_for_form(self, form, base_fields):
        """
        The purpose of this method is to allow one field name to be reliably
        used by two forms only in the narrow case that it actually is the
        same data being repeated in two places.  In other words, two forms
        sharing a field name may only be combined if that field is of the same
        type in both forms, uses the same widget in both forms, has the same
        initial value in both forms, has the same choices (if it is a choice
        field) in both forms, and is not a form id.
        """

        for name, field in form.fields.items():

            # form_id is special because it is built in the create method
            if "form_id" == name and \
               not isinstance(field.widget, forms.HiddenInput) and \
               not isinstance(field.widget, forms.MultiWidget):
                raise ValueError("Fields named 'form_id' must use a HiddenInput widget, "
                                 "or must contain a group of HiddenInput widgets.")
            elif "form_id" in name:
                self._form_ids.append(field)

            elif name not in base_fields:
                # The initial value of the form should be preserved, even if it is not default
                self._initial[name] = form.__getitem__(name).value()
                base_fields[name] = field

            elif base_fields[name].__class__ is not field.__class__:
                raise ValueError("Fields with the same name '%s' are of different "
                                 "types." % name)
            elif base_fields[name].widget.__class__ is not field.widget.__class__:
                raise ValueError("Fields with the same name '%s' use different "
                                     "widgets." % name)
            #elif self._initial[name] != form.initial[name]:
            #    raise ValueError("The initial values of two fields with the same "
            #                     "name '%s' do not match ('%s' vs. '%s')"
            #                     % (name, self._initial[name], form.initial[name]))
            elif hasattr(base_fields[name], 'choices') and \
                 hasattr(field, 'choices') and \
                 set(base_fields[name].choices) != set(field.choices):
                raise ValueError("Choice fields with same name '%s' have different "
                                 "choices." % name)

    def _generate_class(self):
        if not hasattr(self, 'ComboForm'):

            ComboBaseForm = type('ComboBaseForm', (forms.BaseForm,), self._fields)

            class ComboForm(ComboBaseForm, FormMixin):

                @classmethod
                def form_id(self, instance=None):
                    form_ids = ""
                    for form in self._forms:
                        form_ids += "_" + form.__module__ + "." + form.__class__.__name__ + "_"
                        if hasattr(form, "instance") and form.instance is not None:
                            form_ids += "_" + form.instance.__module__ + \
                                        "." + form.instance.__class__.__name__ + "_"
                            if hasattr(form.instance, "pk") and form.instance.pk is not None:
                                form_ids += "_" + str(form.instance.pk)
                    return 'F' + hashlib.md5(form_ids).hexdigest()

                @classmethod
                def form_id_field(self, form_id):
                    widgets = [forms.HiddenInput(),]
                    initial = [form_id,]
                    fields  = [forms.CharField(widget=widgets[0],initial=initial[0])]

                    for field in self._form_ids:
                        fields .append(field)
                        widgets.append(field.widget)
                        initial.append(field.initial)

                    widget = forms.MultiWidget(widgets)

                    # this is here just because compress() needs to be implemented
                    class FormIdField(forms.MultiValueField):
                        def compress(self, data):
                            return data

                    return FormIdField(fields, widget=widget, initial=initial)

                def __init__(self, *args, **kwargs):
                    super(ComboForm, self).__init__(*args, **kwargs)
                    self.initial = self.__class__._initial.copy()

                def full_clean(self):
                    ''' 
                    If it is the same data, two forms with the same field validate differently.
                    Both of these validation outcomes should be included, with dupes removed.
                    The assumption is made that the parent form has already been preped.
                    '''
                    self._errors = forms.util.ErrorDict()
                    for form in self.__class__._forms:
                        for error in form.errors:
                            if error not in self._errors:
                                # use a set here and below to prevent duplicates
                                self._errors[error] = set(form.errors[error])
                            else:
                                self._errors[error] += set(form.errors[error])

                    # convert from the set to the designated error class
                    for error in self._errors:
                        self._errors[error] = self.error_class(self._errors[error])

                    # if there are no errors in the sub-fields, create cleaned_data 
                    if not self._errors:
                        super(ComboForm, self).full_clean()
                    
                def save(self, commit=True):
                    for form in self.__class__._forms:
                        form.save(commit)
                    

            self.ComboForm = ComboForm

    def get_form_class(self):
        return self.ComboForm

    def create_form(self, POST=None, path=None):
        return self.ComboForm.create(POST, path)

# Django's built-in ImageField doesn't work on AppEngine because
# it relies on unavailable PIL APIs. Here's my own version that works.

def image_bytes_are_valid(image_bytes):

    return True

class AppEngineImageField(forms.FileField):
    default_error_messages = {
        'invalid_image': _(u"Upload a valid image. The file you uploaded was either not an image or was a corrupted image."),
    }
    
    def clean(self, data, initial=None):
        raw_file = super(AppEngineImageField, self).clean(data, initial)
        if raw_file is None:
            return None
        elif not data and initial:
            return initial
            
        if hasattr(data, 'read'):
            bytes = data.read()
        else:
            try:
                bytes = data['content']
            except:
                bytes = None
        
        if bytes is None:
            raise forms.ValidationError(self.error_messages['invalid_image'])
        
        if (len(bytes) > 0) and (not image_bytes_are_valid(bytes)):
            raise forms.ValidationError(self.error_messages['invalid_image'])
        
        if hasattr(raw_file, 'seek') and callable(raw_file.seek):
            raw_file.seek(0)
            
        return raw_file

