# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import Peptide, PeptideBatch, Virus, VirusBatch, Antibody, AntibodyBatch, Complex, ComplexBatch, \
    ProcessStep, Step, Spotting, Washing, Drying, Quenching, Blocking, Scanning, Incubating, \
    Process, GalFile, Experiment, RawSpotCollection, RawSpot,SpotCollection, Spot
from .forms import ProcessAdminForm


class PeptideAdmin(admin.ModelAdmin):
    fields = ['sid', 'linker', 'spacer', 'sequence', 'c_terminus', 'name', 'comment']
class VirusAdmin(admin.ModelAdmin):
    fields = ['sid','tax_id', 'subtype', "isolation_country", "collection_date", "strain", "link_db", "comment"]
class AntibodyAdmin(admin.ModelAdmin):
    fields = ['sid', 'target','name', 'link_db', 'comment']
class ComplexAdmin(admin.ModelAdmin):
    fields = ['sid','ligands','comment']



batch_fields = ['sid', 'ligand','concentration', 'buffer', 'ph', 'purity', 'produced_by','production_date', 'comment']

class PeptideBatchAdmin(admin.ModelAdmin):
    fields = batch_fields
class VirusBatchAdmin(admin.ModelAdmin):
    fields = batch_fields
class AntibodyBatchAdmin(admin.ModelAdmin):
    fields = batch_fields
class ComplexBatchAdmin(admin.ModelAdmin):
    fields = batch_fields

class GalFileAdmin(admin.ModelAdmin):
    fields = ['sid', 'file']


class RawSpotCollectionAdmin(admin.ModelAdmin):
    fields = ['sid', 'experiment_type','batch','functionalization','manufacturer', 'process', 'comment','image','gal_file1','gal_file2']

class RawSpotAdmin(admin.ModelAdmin):
    fields = ['raw_spot_collection',"ligand1","ligand2","column", "row"]

class SpotCollectionAdmin(admin.ModelAdmin):
    fields = ["sid", "raw_spot_collection", "image2numeric_version","processing_type", "comment"]

class SpotAdmin(admin.ModelAdmin):
    fields = ["raw_spot", "intensity", "std", "spot_collection"]

class StepAdmin(admin.ModelAdmin):
    model = Step
    fields = ['sid', 'method', 'temperature', 'comment']

class SpottingAdmin(admin.ModelAdmin):
    model = Spotting
    fields = ['sid', 'method', 'temperature', 'comment']

class WashingAdmin(admin.ModelAdmin):
    model = Washing
    fields = ['sid', 'method', 'substance', 'temperature', 'comment']

class DryingAdmin(admin.ModelAdmin):
    model = Drying
    fields = ['sid', 'method', 'substance', 'temperature', 'comment']


class QuenchingAdmin(admin.ModelAdmin):
    model = Quenching
    fields = ['sid', 'method', 'substance', 'temperature', 'comment']

class BlockingAdmin(admin.ModelAdmin):
    model = Blocking
    fields = ['sid', 'method', 'substance', 'temperature', 'comment']

class IncubatingAdmin(admin.ModelAdmin):
    model = Incubating
    fields = ['sid', 'method', 'temperature', 'comment']


class ScanningAdmin(admin.ModelAdmin):
    model = Scanning
    fields = ['sid', 'method', 'temperature', 'comment']


class ProcessAdmin(admin.ModelAdmin):
    # The precious fieldsets.
    fieldsets = (('Basic Info', { 'fields' : ('sid','ordering',)}),)
    # Here's where we override our form
    form = ProcessAdminForm




admin.site.register(Peptide, PeptideAdmin)
admin.site.register(Virus, VirusAdmin)
admin.site.register(Antibody, AntibodyAdmin)
admin.site.register(Complex, ComplexAdmin)


admin.site.register(PeptideBatch, PeptideBatchAdmin)
admin.site.register(AntibodyBatch, AntibodyBatchAdmin)
admin.site.register(VirusBatch, VirusBatchAdmin)
admin.site.register(ComplexBatch, ComplexBatchAdmin)


admin.site.register(Process, ProcessAdmin)
admin.site.register(Step, StepAdmin)


admin.site.register(Spotting, SpottingAdmin)
admin.site.register(Scanning, ScanningAdmin)
admin.site.register(Incubating, IncubatingAdmin)
admin.site.register(Blocking, BlockingAdmin)
admin.site.register(Quenching, QuenchingAdmin)
admin.site.register(Drying, DryingAdmin)
admin.site.register(Washing, WashingAdmin)

admin.site.register(GalFile, GalFileAdmin)

admin.site.register(RawSpotCollection, RawSpotCollectionAdmin)
admin.site.register(SpotCollection, SpotCollectionAdmin)
admin.site.register(Spot, SpotAdmin)
admin.site.register(RawSpot, RawSpotAdmin)





