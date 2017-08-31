import numpy as np
from django import forms
from django.forms import formset_factory

from .models import Peptide, PeptideBatch, Virus, VirusBatch, Antibody, AntibodyBatch, \
    ProcessStep, Step, Spotting, Washing, Drying, Quenching, Blocking, Scanning, Incubating, \
    Process

class OrderedModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    def clean(self, value):
        qs = super(OrderedModelMultipleChoiceField, self).clean(value)
        clauses = ' '.join(['WHEN id=%s THEN %s' % (pk, i) for i, pk in enumerate(value)])
        return qs.filter(pk__in=value).extra(
            select={'ordering': 'CASE %s END' % clauses},
            order_by=('ordering',)
        )

class PeptideForm(forms.ModelForm):
    class Meta:
        model = Peptide
        fields = ['sid', 'linker', 'spacer', 'sequence', 'c_terminus', 'name', 'comment']


class VirusForm(forms.ModelForm):
    class Meta:
        model = Virus
        fields = ['sid','tax_id', 'subtype', "isolation_country", "collection_date", "strain", "link_db", "comment"]


class AntibodyForm(forms.ModelForm):
    class Meta:
        model = Antibody
        fields = ['sid', 'target','name', 'link_db', 'comment']

batch_fields = ['sid', 'ligand','concentration', 'buffer', 'ph', 'purity', 'produced_by','production_date', 'comment']
class PeptideBatchForm(forms.ModelForm):
    class Meta:
        model = PeptideBatch
        fields = batch_fields
class VirusBatchForm(forms.ModelForm):
    class Meta:
        model = VirusBatch
        fields = batch_fields


class AntibodyBatchForm(forms.ModelForm):
    class Meta:
        model = AntibodyBatch
        fields = batch_fields


class ProcessStepForm(forms.ModelForm):
    class Meta:
        model = ProcessStep
        fields = '__all__'

class StepForm(forms.ModelForm):
    class Meta:
        model = Step
        fields = '__all__'



class SpottingForm(forms.ModelForm):
    class Meta:
        model = Spotting
        fields = ['sid', 'method', 'temperature', 'comment']


class WashingForm(forms.ModelForm):
    class Meta:
        model = Washing
        fields = ['sid', 'method', 'substance', 'temperature', 'comment']


class DryingForm(forms.ModelForm):
    class Meta:
        model = Drying
        fields = ['sid', 'method', 'substance', 'temperature', 'comment']


class QuenchingForm(forms.ModelForm):
    class Meta:
        model = Quenching
        fields = ['sid', 'method', 'substance', 'temperature', 'comment']


class BlockingForm(forms.ModelForm):
    class Meta:
        model = Blocking
        fields = ['sid', 'method', 'substance', 'temperature', 'comment']


class IncubatingForm(forms.ModelForm):
    class Meta:
        model = Incubating
        fields = ['sid', 'method', 'temperature', 'comment']
        labels ={
            'temperature':'Temperature',
        }
        help_texts = {
            'temperature': 'In Celsius.',
        }




class ScanningForm(forms.ModelForm):
    class Meta:
        model = Scanning
        fields = '__all__'


class ProcessForm(forms.ModelForm):
    orderer_steps = OrderedModelMultipleChoiceField(Step.objects.all())
    class Meta:
        model = Process
        fields = ['sid']


class ProcessFormUpdate(forms.ModelForm):
    orderer_steps = OrderedModelMultipleChoiceField(Step.objects.all())
    class Meta:
        model = Process
        fields = ['sid']

class Steps2Form(forms.Form):
   step = forms.ModelChoiceField(Step.objects.all())


Steps2FormSet = formset_factory(Steps2Form, extra=1)

