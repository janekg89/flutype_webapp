
from django import forms
from .models import Ligand, LigandBatch, Peptide, PeptideBatch, Virus, VirusBatch

class PeptideForm(forms.ModelForm):
    class Meta:
        model = Peptide
        fields = ['sid','linker','spacer','sequence','c_terminus','name','comment']
class PeptideBatchForm(forms.ModelForm):
    class Meta:
        model = PeptideBatch
        fields = '__all__'