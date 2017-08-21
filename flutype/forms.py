
from django import forms
from .models import Ligand, LigandBatch, Peptide, PeptideBatch, Virus, VirusBatch

class PeptideForm(forms.ModelForm):
    class Meta:
        model = Peptide
        fields = '__all__'

class PeptideBatchForm(forms.ModelForm):
    class Meta:
        model = PeptideBatch
        fields = '__all__'