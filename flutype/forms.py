from django import forms
from .models import Peptide, PeptideBatch, Virus, VirusBatch, Antibody, AntibodyBatch, \
    ProcessStep, Step, Spotting, Washing, Drying, Quenching, Blocking, Scanning, Incubating, \
    Process


class PeptideForm(forms.ModelForm):
    class Meta:
        model = Peptide
        fields = ['sid', 'linker', 'spacer', 'sequence', 'c_terminus', 'name', 'comment']


class VirusForm(forms.ModelForm):
    class Meta:
        model = Virus
        fields = "__all__"


class AntibodyForm(forms.ModelForm):
    class Meta:
        model = Antibody
        fields = "__all__"


class PeptideBatchForm(forms.ModelForm):
    class Meta:
        model = PeptideBatch
        fields = '__all__'


class VirusBatchForm(forms.ModelForm):
    class Meta:
        model = VirusBatch
        fields = '__all__'


class AntibodyBatchForm(forms.ModelForm):
    class Meta:
        model = AntibodyBatch
        fields = '__all__'


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
        fields = '__all__'


class WashingForm(forms.ModelForm):
    class Meta:
        model = Washing
        fields = '__all__'


class DryingForm(forms.ModelForm):
    class Meta:
        model = Drying
        fields = '__all__'


class QuenchingForm(forms.ModelForm):
    class Meta:
        model = Quenching
        fields = '__all__'


class BlockingForm(forms.ModelForm):
    class Meta:
        model = Blocking
        fields = '__all__'


class IncubatingForm(forms.ModelForm):
    class Meta:
        model = Incubating
        fields = '__all__'


class ScanningForm(forms.ModelForm):
    class Meta:
        model = Scanning
        fields = '__all__'


class ProcessForm(forms.ModelForm):
    class Meta:
        model = Process
        fields = '__all__'
