# -*- coding: utf-8 -*-
"""
Admin interface for FluTypeDB.
"""
from __future__ import unicode_literals
from django.contrib import admin
from .models import Peptide, PeptideBatch, Virus, VirusBatch, Antibody, AntibodyBatch, Complex, ComplexBatch, \
    ProcessStep, Step, Spotting, Washing, Drying, Quenching, Blocking, Scanning, Incubating, \
    Process, GalFile, Measurement, RawSpotCollection, RawSpot, SpotCollection, Spot, \
    Buffer, BufferBatch
from .forms import ProcessAdminForm


################################
# Ligands
################################


################################
# Ligands
################################
@admin.register(Peptide)
class PeptideAdmin(admin.ModelAdmin):
    fields = ('sid', 'linker', 'spacer', 'sequence', 'c_terminus', 'name', 'comment')
    list_display = ('sid', 'linker', 'spacer', 'sequence', 'c_terminus', 'name', 'comment')
    list_filter = ('linker', 'spacer', 'sequence')

@admin.register(Virus)
class VirusAdmin(admin.ModelAdmin):
    fields = ['sid', 'tax_id', 'subtype', 'isolation_country', 'collection_date', 'strain', 'link_db', 'comment']
    list_display = ['sid', 'tax_id', 'subtype', 'isolation_country', 'collection_date', 'strain', 'link_db', 'comment']

@admin.register(Antibody)
class AntibodyAdmin(admin.ModelAdmin):
    fields = ['sid', 'target', 'name', 'link_db', 'comment']

@admin.register(Complex)
class ComplexAdmin(admin.ModelAdmin):
    fields = ['sid', 'ligands', 'comment']


@admin.register(Buffer)
class BufferAdmin(admin.ModelAdmin):
    fields = ['sid', 'name', 'comment']


################################
# Ligand Batches
################################
BATCH_FIELDS = ['sid', 'ligand', 'concentration', 'buffer', 'ph', 'purity', 'produced_by', 'production_date', 'comment']

@admin.register(PeptideBatch)
class PeptideBatchAdmin(admin.ModelAdmin):
    fields = BATCH_FIELDS

@admin.register(VirusBatch)
class VirusBatchAdmin(admin.ModelAdmin):
    fields = BATCH_FIELDS

@admin.register(AntibodyBatch)
class AntibodyBatchAdmin(admin.ModelAdmin):
    fields = BATCH_FIELDS

@admin.register(ComplexBatch)
class ComplexBatchAdmin(admin.ModelAdmin):
    fields = BATCH_FIELDS

@admin.register(BufferBatch)
class BufferBatchAdmin(admin.ModelAdmin):
    fields = BATCH_FIELDS


################################
# Spot & Spot Collections
################################
@admin.register(RawSpotCollection)
class RawSpotCollectionAdmin(admin.ModelAdmin):
    fields = ['sid', 'experiment_type', 'batch', 'functionalization', 'manufacturer', 'process', 'comment',
              'image', 'gal_file1', 'gal_file2']

@admin.register(RawSpot)
class RawSpotAdmin(admin.ModelAdmin):
    fields = ['raw_spot_collection', 'ligand1', 'ligand2', 'column', 'row']

@admin.register(SpotCollection)
class SpotCollectionAdmin(admin.ModelAdmin):
    fields = ['sid', 'raw_spot_collection', 'image2numeric_version', 'processing_type', 'comment']

@admin.register(Spot)
class SpotAdmin(admin.ModelAdmin):
    fields = ['raw_spot', 'intensity', 'std', 'spot_collection']


################################
# Process & Process Steps
################################
STEP_FIELDS = ['sid', 'method', 'temperature', 'comment']

@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    # The precious fieldsets.
    fieldsets = (('Basic Info', {'fields': ('sid', 'ordering',)}),)
    # Here's where we override our form
    form = ProcessAdminForm

@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    model = Step
    fields = STEP_FIELDS

@admin.register(Spotting)
class SpottingAdmin(admin.ModelAdmin):
    model = Spotting
    fields = STEP_FIELDS

@admin.register(Scanning)
class ScanningAdmin(admin.ModelAdmin):
    model = Scanning
    fields = STEP_FIELDS

@admin.register(Washing)
class WashingAdmin(admin.ModelAdmin):
    model = Washing
    fields = STEP_FIELDS + ['substance']

@admin.register(Drying)
class DryingAdmin(admin.ModelAdmin):
    model = Drying
    fields = STEP_FIELDS + ['substance']

@admin.register(Quenching)
class QuenchingAdmin(admin.ModelAdmin):
    model = Quenching
    fields = STEP_FIELDS + ['substance']

@admin.register(Blocking)
class BlockingAdmin(admin.ModelAdmin):
    model = Blocking
    fields = STEP_FIELDS + ['substance']

@admin.register(Incubating)
class IncubatingAdmin(admin.ModelAdmin):
    model = Incubating
    fields = STEP_FIELDS

################################
# Gal files
################################
@admin.register(GalFile)
class GalFileAdmin(admin.ModelAdmin):
    fields = ['sid', 'file']
