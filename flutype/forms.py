# -*- coding: utf-8 -*-
"""
Forms
"""
from django import forms
from django.urls import reverse
from django.contrib import admin
from django.utils.safestring import mark_safe
from measurement.measures import Volume, Mass
from .models import Peptide, PeptideBatch, Virus, VirusBatch, Antibody, AntibodyBatch, Complex, \
    ProcessStep, Step, Spotting, Washing, Drying, Quenching, Blocking, Scanning, Incubating, \
    Process, GalFile, Measurement, RawSpotCollection, RawSpot,SpotCollection, Spot, ComplexBatch, Study, \
    IncubatingAnalyt, RawDoc, Buffer, BufferBatch, Concentration, MeasurementType
from django_measurement.forms import MeasurementField
from django.forms.utils import ErrorList
from .helper import camel_case_split
from django.utils.timezone import localtime, now

class OrderedModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def clean(self, value):
        qs = super(OrderedModelMultipleChoiceField, self).clean(value)
        clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(value)])
        return qs.filter(pk__in=value).extra(
            select={'ordering': 'CASE %s END' % clauses},
            order_by=('ordering',)
        )

class BaseForm(forms.ModelForm):

    @property
    def hr_classname(self):
        form_name = self.Meta.model.__name__
        return camel_case_split(form_name)

class URLRedirectBaseForm(BaseForm):

    @property
    def url_redirect(self):
        return self.Meta.model.url()


class MeasurementForm(URLRedirectBaseForm):
    class Meta:
        model = RawSpotCollection
        fields = ["sid",'batch_sid','user','measurement_type','functionalization','manufacturer',"comment"]
        widgets = {
            'sid': forms.TextInput(attrs={'placeholder': 'Sid', 'class':'form-control'}),
            'batch_sid': forms.TextInput(attrs={'placeholder': 'Batch Sid', 'class': 'form-control'}),
            'measurement_type': forms.Select(attrs={'class':'form-control'}),
            'user': forms.Select(attrs={'class':'form-control'}),
            'manufacturer': forms.Select(attrs={'class': 'form-control'}),
            'functionalization': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
        }




class RawDocForm(BaseForm):
    class Meta:
        model = RawDoc
        fields = '__all__'


class GalFileForm(BaseForm):
    class Meta:
        model = GalFile
        fields = ['rows_in_tray', 'columns_in_tray', 'vertical_trays', 'horizontal_trays']


class StudyForm(URLRedirectBaseForm):
    """ Form for Study. """
    date = forms.DateField(required=True, widget=forms.TextInput(attrs=
    {
        'data-provide': 'datepicker'
    }))

    class Meta:
        model = Study
        fields = ["sid","description","status","user","comment", "date"]
        widgets = {
            'sid': forms.TextInput(attrs={'placeholder': 'Sid', 'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }




class PeptideForm(URLRedirectBaseForm):
    """ Form for Peptide. """
    class Meta:
        model = Peptide
        fields = ['sid', 'linker', 'spacer', 'sequence', 'c_terminus', 'name', 'comment']


class BufferForm(URLRedirectBaseForm):
    """ Form for Buffer. """
    class Meta:
        model = Buffer
        fields = ['sid', 'name', 'comment']


class ComplexForm(URLRedirectBaseForm):
    """ Form for Complex. """
    class Meta:
        model = Complex
        fields = ['sid', 'complex_ligands', 'comment']


class VirusForm(URLRedirectBaseForm):
    """ Form for virus.
    collection_date = forms.DateField(widget=forms.TextInput(attrs=
    {
        'class': 'datepicker'
    }))
    """
    class Meta:
        model = Virus
        fields = ['sid', 'tax_id', 'subtype', "isolation_country", "collection_date", "strain", "link_db", "comment"]


class AntibodyForm(URLRedirectBaseForm):
    class Meta:
        model = Antibody
        fields = ['sid', 'target', 'name', 'link_db', 'comment']

########################################################################################################################
# Configuration for Batch Forms
PRODUCTION_DATE = forms.DateField(initial=localtime(now()).date(),widget=forms.TextInput(attrs=
    {
        'data-provide': 'datepicker'
    }))

BATCH_FIELDS = ['sid', 'ligand', 'concentration', 'concentration_unit', 'buffer', 'ph', 'purity',
                'produced_by', 'production_date', 'comment','stock']
########################################################################################################################

class BufferBatchForm(URLRedirectBaseForm):
    stock = forms.BooleanField(initial=True, widget=forms.HiddenInput())
    production_date = PRODUCTION_DATE
    class Meta:
        model = BufferBatch
        fields = ['sid', 'buffer', 'ph', 'produced_by', 'production_date', 'comment']




class FormCleanMixin(URLRedirectBaseForm):
    stock = forms.BooleanField(initial=True, widget=forms.HiddenInput())
    production_date = PRODUCTION_DATE

    def clean(self):
        if self.cleaned_data.get('concentration') and not self.cleaned_data.get('concentration_unit'):
            self.errors['concentration_unit'] = ErrorList(["A concentration unit is required if concentration present"])

        if not self.cleaned_data.get('concentration') and self.cleaned_data.get('concentration_unit'):
            self.errors['concentration_unit'] = ErrorList(
                ["A concentration Unit should only be present if there\'s a Concentration"])


class PeptideBatchForm(FormCleanMixin):
    """ Form for PeptideBatch. """
    def __init__(self, *args, **kwargs):
        super(PeptideBatchForm, self).__init__(*args, **kwargs)
        self.fields['ligand'].queryset = Peptide.objects.all()
        self.fields['ligand'].label = "Peptide"
        self.fields['ligand'].help_text = "go to <a href='{}'>peptides list </a>.".format(reverse('peptides'))
        self.fields['ligand'].required = True

    class Meta:
        model = PeptideBatch
        fields = BATCH_FIELDS


class ComplexBatchForm(FormCleanMixin):
    """ Form for ComplexBatch. """
    def __init__(self, *args, **kwargs):
        super(ComplexBatchForm, self).__init__(*args, **kwargs)
        self.fields['ligand'].queryset = Complex.objects.all()
        self.fields['ligand'].label = "Complex"
        self.fields['ligand'].help_text = "go to <a href='{}'>complexes list </a>.".format(reverse('complexes'))
        self.fields['ligand'].required = True

    class Meta:
        model = ComplexBatch
        fields = BATCH_FIELDS


class VirusBatchForm(FormCleanMixin):
    """ Form for VirusBatch. """
    def __init__(self, *args, **kwargs):
        super(VirusBatchForm, self).__init__(*args, **kwargs)
        self.fields['ligand'].queryset = Virus.objects.all()
        self.fields['ligand'].label = "Virus"
        self.fields['ligand'].help_text = "go to <a href='{}'>viruses list </a>.".format(reverse('viruses'))
        self.fields['ligand'].required = True

    class Meta:
        model = VirusBatch
        fields = BATCH_FIELDS +['passage_history','active']


class AntibodyBatchForm(FormCleanMixin):
    """ Form for AntibodyBatch. """
    def __init__(self, *args, **kwargs):
        super(AntibodyBatchForm, self).__init__(*args, **kwargs)
        self.fields['ligand'].queryset = Antibody.objects.all()
        self.fields['ligand'].label = "Antibody"
        self.fields['ligand'].help_text = "go to <a href='{}'>antibodies list </a>.".format(reverse('antibodies'))
        self.fields['ligand'].required = True

    class Meta:
        model = AntibodyBatch
        fields = BATCH_FIELDS


BASIC_STEP_FIELDS = ['sid', 'method', 'temperature', 'comment']


class ProcessStepForm(URLRedirectBaseForm):
    """ Form for ProcessStep. """
    class Meta:
        model = ProcessStep
        fields = ['step', 'index']


class StepForm(URLRedirectBaseForm):
    """ Form for Step. """
    class Meta:
        model = Step
        fields = BASIC_STEP_FIELDS
        help_texts = {
            'temperature': 'temperature in °C',
            'duration': 'duration in [hh:mm:ss]',
        }


class SpottingForm(URLRedirectBaseForm):
    """ Form for Spotting. """
    class Meta(StepForm.Meta):
        model = Spotting


class WashingForm(URLRedirectBaseForm):
    """ Form for Washing. """
    class Meta(StepForm.Meta):
        model = Washing
        fields = ['sid', 'method', 'substance', 'temperature', 'duration', 'comment']


class DryingForm(URLRedirectBaseForm):
    """ Form for Drying. """
    class Meta(StepForm.Meta):
        model = Drying
        fields = ['sid', 'method', 'substance', 'temperature', 'duration', 'comment']


class QuenchingForm(URLRedirectBaseForm):
    class Meta(StepForm.Meta):
        model = Quenching
        fields = ['sid', 'method', 'substance', 'temperature', 'duration', 'comment']


class BlockingForm(URLRedirectBaseForm):
    class Meta(StepForm.Meta):
        model = Blocking
        fields = ['sid', 'method', 'substance', 'temperature', 'duration', 'comment']


class IncubatingForm(URLRedirectBaseForm):
    class Meta(StepForm.Meta):
        model = Incubating
        fields = ['sid', 'method', 'temperature', 'duration', 'comment']



# FIXME: naming analyt -> analyte
class IncubatingAnalytForm(URLRedirectBaseForm):
    class Meta(StepForm.Meta):
        model = IncubatingAnalyt
        fields = ['sid', 'method', 'temperature','duration', 'comment']


class ScanningForm(URLRedirectBaseForm):
    class Meta(StepForm.Meta):
        model = Scanning
        fields = '__all__'


class ProcessForm(URLRedirectBaseForm):
    class Meta:
        model = Process
        fields = ['sid', 'unique_ordering']


class ProcessFormUpdate(URLRedirectBaseForm):
    orderer_steps = OrderedModelMultipleChoiceField(Step.objects.all())
    class Meta:
        model = Process
        fields = ['sid']

class Steps2Form(forms.Form):
   step = forms.ModelChoiceField(Step.objects.values_list('sid', flat=True))
   method = forms.ModelChoiceField(Step.objects.values_list('method', flat=True))



# Generates a function that sequentially calls the two functions that were passed to it
def func_concat(old_func, new_func):
    def function():
        old_func()
        new_func()
    return function


# A dummy widget to be replaced with your own.
class OrderedManyToManyWidget(forms.widgets.TextInput):
    pass


# A simple CharField that shows a comma-separated list of contestant IDs.
class OrderedStepField(forms.CharField):
    widget = OrderedManyToManyWidget()


class ProcessAdminForm(forms.models.ModelForm):
    # Any fields declared here can be referred to in the "fieldsets" or
    # "fields" of the ModelAdmin. It is crucial that our custom field does not
    # use the same name as the m2m field field in the model ("Step" in
    # our example).
    ordering = OrderedStepField()

    class Meta:
        model = Process
        fields = '__all__'

    # Override init so we can populate the form field with the existing data.
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        # See if we are editing an existing Process. If not, there is nothing
        # to be done.
        if instance and instance.pk:
            # Get a list of all the IDs of the contestants already specified
            # for this contest.
            steps = ProcessStep.objects.filter(process=instance).order_by('index').values_list('step_id', flat=True)
            # Make them into a comma-separated string, and put them in our
            # custom field.
            self.base_fields['ordering'].initial = ','.join(map(str, steps))
            # Depending on how you've written your widget, you can pass things
            # like a list of available contestants to it here, if necessary.
        super(ProcessAdminForm, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        # This "commit" business complicates things somewhat. When true, it
        # means that the model instance will actually be saved and all is
        # good. When false, save() returns an unsaved instance of the model.
        # When save() calls are made by the Django admin, commit is pretty
        # much invariably false, though I'm not sure why. This is a problem
        # because when creating a new Process instance, it needs to have been
        # saved in the DB and have a PK, before we can create ProcessStep.
        # Fortunately, all models have a built-in method called save_m2m()
        # which will always be executed after save(), and we can append our
        # ProcessStep-creating code to the existing same_m2m() method.
        commit = kwargs.get('commit', True)
        # Save the Process and get an instance of the saved model
        instance = super(ProcessAdminForm, self).save(*args, **kwargs)
        # This is known as a lexical closure, which means that if we store
        # this function and execute it later on, it will execute in the same
        # context (i.e. it will have access to the current instance and self).

        def save_m2m():
            # This is really naive code and should be improved upon,
            # especially in terms of validation, but the basic gist is to make
            # the needed ContestResults. For now, we'll just delete any
            # existing ContestResults for this Contest and create them anew.

            ProcessStep.objects.filter(process=instance).delete()
            # Make a list of (rank, contestant ID) tuples from the comma-
            # -separated list of contestant IDs we get from the results field.
            formdata = enumerate(map(int, self.cleaned_data['ordering'].split(',')), 1)
            for order, step in formdata:
                ProcessStep.objects.create(process=instance, step_id=step, index=order)
        if commit:
            # If we're committing (fat chance), simply run the closure.
            save_m2m()
        else:
            # Using a function concatenator, ensure our save_m2m closure is
            # called after the existing save_m2m function (which will be
            # called later on if commit is False).
            self.save_m2m = func_concat(self.save_m2m, save_m2m)
            # Return the instance like a good save() method.
        return instance
