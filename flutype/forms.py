
from django import forms
from .models import Ligand, LigandBatch, Peptide, PeptideBatch, Virus, VirusBatch, Antibody

class PeptideForm(forms.ModelForm):
    class Meta:
        model = Peptide
        fields = ['sid','linker','spacer','sequence','c_terminus','name','comment']

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