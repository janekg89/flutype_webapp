# -*- coding: utf-8 -*-

import numpy as np
from django import forms
from django.urls import reverse
from django.contrib import admin
from django.utils.safestring import mark_safe
from measurement.measures import Volume, Mass
from .models import Peptide, PeptideBatch, Virus, VirusBatch, Antibody, AntibodyBatch, Complex, \
    ProcessStep, Step, Spotting, Washing, Drying, Quenching, Blocking, Scanning, Incubating, \
    Process, GalFile, Measurement, RawSpotCollection, RawSpot,SpotCollection, Spot, ComplexBatch, Study, \
    IncubatingAnalyt, RawDoc, Buffer, BufferBatch, Concentration
from django_measurement.forms import MeasurementField
from django.forms.utils import ErrorList



class OrderedModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def clean(self, value):
        qs = super(OrderedModelMultipleChoiceField, self).clean(value)
        clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(value)])
        return qs.filter(pk__in=value).extra(
            select={'ordering': 'CASE %s END' % clauses},
            order_by=('ordering',)
        )

class RawDocForm(forms.ModelForm):
    class Meta:
        model = RawDoc
        fields = '__all__'

class GalFileForm(forms.ModelForm):
    class Meta:
        model = GalFile
        fields = ['rows_in_tray','columns_in_tray','vertical_trays','horizontal_trays']


class StudyForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = '__all__'


class PeptideForm(forms.ModelForm):
    class Meta:
        model = Peptide
        fields = ['sid', 'linker', 'spacer', 'sequence', 'c_terminus', 'name', 'comment']

class BufferForm(forms.ModelForm):
    class Meta:
        model = Buffer
        fields = '__all__'

class BufferBatchForm(forms.ModelForm):
    class Meta:
        model = BufferBatch
        fields = ['sid', 'buffer', 'ph','produced_by','production_date', 'comment']


class ComplexForm(forms.ModelForm):

    class Meta:
        model = Complex
        fields = ['sid', 'complex_ligands', 'comment']


class VirusForm(forms.ModelForm):
    class Meta:
        model = Virus
        fields = ['sid', 'tax_id', 'subtype', "isolation_country", "collection_date", "strain", "link_db", "comment"]


class AntibodyForm(forms.ModelForm):
    class Meta:
        model = Antibody
        fields = ['sid', 'target', 'name', 'link_db', 'comment']

batch_fields = ['sid', 'ligand', 'concentration','concentration_unit', 'buffer', 'ph', 'purity', 'produced_by','production_date', 'comment']


class FormCleanMixin(forms.ModelForm):

    def clean(self):
        if self.cleaned_data.get('concentration') and not self.cleaned_data.get('concentration_unit'):
            self.errors['concentration_unit'] = ErrorList(["A concentration unit is required if concentration present"])

        if not self.cleaned_data.get('concentration') and self.cleaned_data.get('concentration_unit'):
            self.errors['concentration_unit'] = ErrorList(
                ["A concentration Unit should only be present if there\'s a Concentration"])


class PeptideBatchForm(FormCleanMixin):

    def __init__(self, *args, **kwargs):
        super(PeptideBatchForm, self).__init__(*args, **kwargs)
        self.fields['ligand'].queryset = Peptide.objects.all()
        self.fields['ligand'].label = "Peptide"
        self.fields['ligand'].help_text = "go to <a href='{}'>peptides list </a>.".format(reverse('peptides'))
        self.fields['ligand'].required = True

    class Meta:
        model = PeptideBatch
        fields = batch_fields




class ComplexBatchForm(FormCleanMixin):

    def __init__(self, *args, **kwargs):
        super(ComplexBatchForm, self).__init__(*args, **kwargs)
        self.fields['ligand'].queryset = Complex.objects.all()
        self.fields['ligand'].label = "Complex"
        self.fields['ligand'].help_text = "go to <a href='{}'>complexes list </a>.".format(reverse('complexes'))
        self.fields['ligand'].required = True

    class Meta:
        model = ComplexBatch
        fields = batch_fields


class VirusBatchForm(FormCleanMixin):
    def __init__(self, *args, **kwargs):
        super(VirusBatchForm, self).__init__(*args, **kwargs)
        self.fields['ligand'].queryset = Virus.objects.all()
        self.fields['ligand'].label = "Virus"
        self.fields['ligand'].help_text = "go to <a href='{}'>viruses list </a>.".format(reverse('viruses'))
        self.fields['ligand'].required = True


    class Meta:
        model = VirusBatch
        fields = batch_fields


class AntibodyBatchForm(FormCleanMixin):

    def __init__(self, *args, **kwargs):
        super(AntibodyBatchForm, self).__init__(*args, **kwargs)
        self.fields['ligand'].queryset = Antibody.objects.all()
        self.fields['ligand'].label = "Antibody"
        self.fields['ligand'].help_text = "go to <a href='{}'>antibodies list </a>.".format(reverse('antibodies'))
        self.fields['ligand'].required = True



    class Meta:
        model = AntibodyBatch
        fields = batch_fields

basic_step_fields= ['sid','method','temperature','comment']


class ProcessStepForm(forms.ModelForm):
    class Meta:
        model = ProcessStep
        fields = ['step','index']


class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = basic_step_fields
        help_texts = {
            'temperature': 'temeperature in °C',
        }



class SpottingForm(forms.ModelForm):
    class Meta(StepForm.Meta):
        model = Spotting


class WashingForm(forms.ModelForm):
    class Meta(StepForm.Meta):
        model = Washing
        fields  = ['sid', 'method', 'substance', 'temperature', 'comment']


class DryingForm(forms.ModelForm):
    class Meta(StepForm.Meta):
        model = Drying
        fields = ['sid', 'method', 'substance', 'temperature', 'comment']


class QuenchingForm(forms.ModelForm):
    class Meta(StepForm.Meta):
        model = Quenching
        fields = ['sid', 'method', 'substance', 'temperature', 'comment']


class BlockingForm(forms.ModelForm):
    class Meta(StepForm.Meta):
        model = Blocking
        fields = ['sid', 'method', 'substance', 'temperature', 'comment']


class IncubatingForm(forms.ModelForm):
    class Meta(StepForm.Meta):
        model = Incubating
        fields = ['sid', 'method', 'temperature', 'comment']



# FIXME: naming analyt -> analyte
class IncubatingAnalytForm(forms.ModelForm):
    class Meta(StepForm.Meta):
        model = IncubatingAnalyt
        fields = ['sid', 'method', 'temperature', 'comment']



class ScanningForm(forms.ModelForm):
    class Meta(StepForm.Meta):
        model = Scanning
        fields = '__all__'


class ProcessForm(forms.ModelForm):
    class Meta:
        model = Process
        fields = ['sid', 'unique_ordering']


class ProcessFormUpdate(forms.ModelForm):
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




