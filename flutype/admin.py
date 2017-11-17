# -*- coding: utf-8 -*-
"""
Admin interface for FluTypeDB.
"""
from __future__ import unicode_literals
from django.contrib import admin
from .models import Peptide, PeptideBatch, Virus, VirusBatch, Antibody, AntibodyBatch, Complex, ComplexBatch, \
    ProcessStep, Step, Spotting, Washing, Drying, Quenching, Blocking, Scanning, Incubating, \
    Process, GalFile, Measurement, RawSpotCollection, RawSpot,SpotCollection, Spot
from .forms import ProcessAdminForm


################################
# Ligands
################################

class PeptideAdmin(admin.ModelAdmin):
    fields = ['sid', 'linker', 'spacer', 'sequence', 'c_terminus', 'name', 'comment']

class VirusAdmin(admin.ModelAdmin):
    fields = ['sid', 'tax_id', 'subtype', "isolation_country", "collection_date", "strain", "link_db", "comment"]

class AntibodyAdmin(admin.ModelAdmin):
    fields = ['sid', 'target', 'name', 'link_db', 'comment']

class ComplexAdmin(admin.ModelAdmin):
    fields = ['sid', 'ligands', 'comment']

admin.site.register(Peptide, PeptideAdmin)
admin.site.register(Virus, VirusAdmin)
admin.site.register(Antibody, AntibodyAdmin)
admin.site.register(Complex, ComplexAdmin)


################################
# Ligand Batches
################################

BATCH_FIELDS = ['sid', 'ligand', 'concentration', 'buffer', 'ph', 'purity', 'produced_by', 'production_date', 'comment']

class PeptideBatchAdmin(admin.ModelAdmin):
    fields = BATCH_FIELDS
class VirusBatchAdmin(admin.ModelAdmin):
    fields = BATCH_FIELDS
class AntibodyBatchAdmin(admin.ModelAdmin):
    fields = BATCH_FIELDS
class ComplexBatchAdmin(admin.ModelAdmin):
    fields = BATCH_FIELDS

admin.site.register(PeptideBatch, PeptideBatchAdmin)
admin.site.register(AntibodyBatch, AntibodyBatchAdmin)
admin.site.register(VirusBatch, VirusBatchAdmin)
admin.site.register(ComplexBatch, ComplexBatchAdmin)


################################
# Gal files
################################

class GalFileAdmin(admin.ModelAdmin):
    fields = ['sid', 'file']

admin.site.register(GalFile, GalFileAdmin)


################################
# Spot & Spot Collections
################################

class RawSpotCollectionAdmin(admin.ModelAdmin):
    fields = ['sid', 'experiment_type','batch','functionalization','manufacturer', 'process', 'comment',
              'image', 'gal_file1', 'gal_file2']

class RawSpotAdmin(admin.ModelAdmin):
    fields = ['raw_spot_collection', "ligand1", "ligand2", "column", "row"]

class SpotCollectionAdmin(admin.ModelAdmin):
    fields = ["sid", "raw_spot_collection", "image2numeric_version", "processing_type", "comment"]

class SpotAdmin(admin.ModelAdmin):
    fields = ["raw_spot", "intensity", "std", "spot_collection"]

admin.site.register(RawSpotCollection, RawSpotCollectionAdmin)
admin.site.register(SpotCollection, SpotCollectionAdmin)
admin.site.register(Spot, SpotAdmin)
admin.site.register(RawSpot, RawSpotAdmin)


################################
# Process & Process Steps
################################

class ProcessAdmin(admin.ModelAdmin):
    # The precious fieldsets.
    fieldsets = (('Basic Info', {'fields': ('sid', 'ordering',)}),)
    # Here's where we override our form
    form = ProcessAdminForm

STEP_FIELDS = ['sid', 'method', 'temperature', 'comment']

class StepAdmin(admin.ModelAdmin):
    model = Step
    fields = STEP_FIELDS

admin.site.register(Process, ProcessAdmin)
admin.site.register(Step, StepAdmin)


class SpottingAdmin(admin.ModelAdmin):
    model = Spotting
    fields = STEP_FIELDS

class ScanningAdmin(admin.ModelAdmin):
    model = Scanning
    fields = STEP_FIELDS

class WashingAdmin(admin.ModelAdmin):
    model = Washing
    fields = STEP_FIELDS + ['substance']

class DryingAdmin(admin.ModelAdmin):
    model = Drying
    fields = STEP_FIELDS + ['substance']

class QuenchingAdmin(admin.ModelAdmin):
    model = Quenching
    fields = STEP_FIELDS + ['substance']

class BlockingAdmin(admin.ModelAdmin):
    model = Blocking
    fields = STEP_FIELDS + ['substance']

class IncubatingAdmin(admin.ModelAdmin):
    model = Incubating
    fields = STEP_FIELDS


admin.site.register(Spotting, SpottingAdmin)
admin.site.register(Scanning, ScanningAdmin)
admin.site.register(Incubating, IncubatingAdmin)
admin.site.register(Blocking, BlockingAdmin)
admin.site.register(Quenching, QuenchingAdmin)
admin.site.register(Drying, DryingAdmin)
admin.site.register(Washing, WashingAdmin)
