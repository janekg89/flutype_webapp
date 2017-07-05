# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# FIXME: NOT -> NA
# FIXME: Rename spreadsheets in accordance with model name
# FIXME: use classes in ForeignKeys instead of strings

class User(models.Model):
    """
    User model
    """
    # FIXME: use the django user model: see https://docs.djangoproject.com/en/1.11/topics/auth/
    name = models.CharField(max_length=50)


class Peptide(models.Model):
    """
    Pepide model
    """
    # FIXME: name ids for models similar, i.e. id_pep, id_tax, better one name like sid
    # FIXME: list sid as first field
    id_pep = models.CharField(max_length=15, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    linker = models.CharField(max_length=50, blank=True, null=True)
    spacer = models.CharField(max_length=50, blank=True, null=True)
    sequence = models.CharField(max_length=50, blank=True, null=True)
    c_terminus = models.CharField(max_length=50, blank=True, null=True)
    pep_type = models.ForeignKey("Peptide_type", blank=True, null=True)
    # FIXME: comment missing


class Peptide_type(models.Model):
    """
    peptide type model
    """
    p_types = models.CharField(max_length=30)


class Virus(models.Model):
    """
    virus model
    """
    subgroup = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    date_of_appearance = models.CharField(max_length=10, blank=True, null=True)
    strain = models.CharField(max_length=50, blank=True, null=True)
    tax_id = models.CharField(max_length=15, blank=True, null=True)


class Buffer(models.Model):
    """
    buffer model
    """
    name = models.CharField(max_length=50)


# FIXME: pH -> ph
class Batch(models.Model):
    """
    Batch model as abstract class not stored in the database
    """
    concentration = models.FloatField(validators=[MinValueValidator(0)],
                                      blank=True, null=True)
    buffer = models.ForeignKey("Buffer", blank=True, null=True)
    pH = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(14)],
                           blank=True, null=True)
    purity = models.FloatField(validators=[MinValueValidator(0)],
                               blank=True, null=True)
    produced_by = models.ForeignKey("User", blank=True, null=True)
    production_date = models.DateField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    class Meta:
        abstract = True


# FIXME: classes as camelcase: -> VirusBatch
class Virus_batch(Batch):
    """
    Virus batch model
    """
    v_batch_id = models.CharField(max_length=20, blank=True, null=True)
    virus = models.ForeignKey("Virus",blank=True, null=True)
    passage_history = models.CharField(max_length=50, blank= True ,null=True)
    active = models.NullBooleanField(blank=True, null=True)
    labeling = models.CharField(max_length=50, blank=True,null=True)


class Peptide_batch(Batch):
    """
    peptide batch model
    """
    p_batch_id = models.CharField(max_length=20)
    peptide = models.ForeignKey("Peptide", blank=True, null=True)


class Substance(models.Model):
    """
    substance model
    """
    name = models.CharField(max_length=50,blank=True,null=True)


# FIXME: create enum with allowed values
'''
class ParameterType(enum.Enum):
    GLOBAL_PARAMETER = 1
    BOUNDARY_INIT = 2
    FLOATING_INIT = 3
    NONE_SBML_PARAMETER = 4
    labels = {
        GLOBAL_PARAMETER: 'GLOBAL_PARAMETER',
        BOUNDARY_INIT: 'BOUNDARY_INIT',
        FLOATING_INIT: 'FLOATING_INIT',
        NONE_SBML_PARAMETER: 'NONE_SBML_PARAMETER'
    }    

class Parameter(models.Model):
    key = models.CharField(max_length=50)
    value = models.FloatField()
    unit = models.CharField(max_length=50)
    parameter_type = enum.EnumField(ParameterType)

'''
class Holder_type(models.Model):
    """
    holder type model
    """
    holder_type=models.CharField(max_length=30,blank=True,null=True)

class Manufacturer(models.Model):
    """
    manufacturer model
    """
    name = models.CharField(max_length=30, null=True , blank=True)


class Spot(models.Model):
    """
    spot model
    """
    peptide_batch = models.ForeignKey(Peptide_batch)
    virus_batch = models.ForeignKey("Virus_batch")
    sample_holder = models.ForeignKey("Sample_holder")
    column = models.IntegerField()
    row = models.IntegerField()
    replica = models.IntegerField(null=True, blank=True)
    ############in results#########################
    intensity = models.FloatField(null=True, blank=True)
    std = models.FloatField(null=True, blank=True)


# FIXME: better name, SpotCollection
# FIXME: charge -> batch
class Sample_holder(models.Model):
    """
    sample holder model
    """
    s_id = models.CharField(max_length=20)
    charge = models.CharField(max_length=20, null=True, blank=True)
    holder_type = models.ForeignKey("Holder_type")
    functionalization = models.ForeignKey("Substance")
    manufacturer = models.ForeignKey("Manufacturer")
    image = models.ImageField(blank=True, null=True)  #todo: how to save ?
    image2numeric_version = models.FloatField(default=0.1)
    process = models.OneToOneField("Process", blank=True, null=True)

##########################################################


class Treatment(models.Model):
    treatment_id = models.CharField(max_length=10,null=True, blank=True)
    method = models.CharField(max_length=50, null=True, blank=True)
    order = models.IntegerField(blank=True, null=True)
    date_time = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey("User", null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        abstract = True


class Washing(Treatment):
    substance = models.CharField(max_length=50, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)


class Drying(Treatment):
    substance = models.CharField(max_length=50, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)


class Spotting(Treatment):
    order = models.IntegerField(default=0,blank=True, null=True)


class Incubating(Treatment):
    duration = models.DurationField(null=True, blank=True)


class Quenching(Treatment):
    duration = models.DurationField(null=True, blank=True)
    substance = models.CharField(max_length=50, null=True, blank=True)


class Process(models.Model):
    washing = models.ManyToManyField("Washing")
    drying = models.ManyToManyField("Drying")
    spotting = models.ManyToManyField("Spotting")
    incubating = models.ManyToManyField("Incubating")
    quenching = models.ManyToManyField("Quenching")

######################################################################



