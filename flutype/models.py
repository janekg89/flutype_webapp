# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
# Create your models here.
"""
class Process(models.Model):
    sample_holder = models.OneToOneField("Sample_holder")
    spotting = models.OneToOneField("Spotting", blank=True)
    quenching = models.OneToOneField("Quenching",blank=True)
    incubating = models.OneToOneField("Incubating", blank=True)
    result = models.OneToOneField("Result", blank=True)

class Sample_holder(models.Model):
    id = models.CharField()
    holder_type = models.ForeignKey("Holder_type")
    functionalization = models.ForeignKey("Substance")
    manufacturer = models.ForeignKey("Manufacturer")
    spot = models.ManyToManyField("Spot", through="Grid")

class Grid(models.Model):
    column = models.IntegerField()
    row = models.IntegerField()


class Holder_type():
    holder_type=models.CharField()

class Manufacturer():
    name = models.CharField()


class Spot(models.Model):
    peptide = models.ForeignKey("Peptide")
    virus = models.ForeignKey("Virus")
    
class Treatment(models.Model):
    name = models.CharField()
    substance = models.CharField(blank = True)
    method = models.CharField()
    date_time = models.DateTimeField()
    duration = models.DurationField()
    comment = models.TextField()
    #order = models.IntegerField(blank =True)


class Spotting(Treatment):
    #todo: make a through relation with when and maybe kind of treatment
    washing = models.ManyToManyField(Treatment)
    drying = models.ManyToManyField(Treatment)


class Quenching(Treatment):
    washing = models.ManyToManyField(Treatment)
    drying = models.ManyToManyField(Treatment)

class Incubating(Treatment):
    washing = models.ManyToManyField(Treatment)
    drying = models.ManyToManyField(Treatment)

class Substance(models.Model):
    name = models.CharField(max_length=50)
    concentration = models.FloatField(validators=[MinValueValidator(0)],
                                      blank=True)

"""
class User(models.Model):
    name = models.CharField(max_length=50)

class Peptide(models.Model):
    id_pep = models.CharField(max_length=15, null=True)
    name = models.CharField(max_length=50,blank=True, null=True)
    linker = models.CharField(max_length=50,blank=True, null=True)
    spacer = models.CharField(max_length=50,blank=True, null=True)
    sequence = models.CharField(max_length=50,blank=True, null=True)
    c_terminus = models.CharField(max_length=50,blank=True, null=True)
    pep_type =models.ForeignKey("Peptide_type",blank=True, null=True)

class Peptide_type(models.Model):
    p_types = models.CharField(max_length=30)

class Virus(models.Model):
    subgroup = models.CharField(max_length=50,blank=True, null=True)
    country = models.CharField(max_length=50,blank=True, null=True)
    date_of_appearance = models.CharField(max_length=10,blank=True, null=True)
    strain = models.CharField(max_length=50,blank=True, null=True)
    tax_id = models.CharField(max_length=15,blank=True, null=True)


class Buffer(models.Model):
    name = models.CharField(max_length=50)


class Batch(models.Model):
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



class Peptide_batch(models.Model):
    batch = models.ForeignKey("Batch",blank=True, null=True)
    peptide = models.ForeignKey("Peptide", blank=True, null=True)

class Virus_batch(Batch):
    virus = models.ForeignKey("Virus",blank=True, null=True)
    batch = models.ForeignKey("Batch",blank=True, null=True,related_name="batch_of_virus")
    passage_history = models.CharField(max_length=50, blank= True ,null=True )
    active = models.NullBooleanField(blank=True, null=True)
    labeling = models.CharField(max_length=50,blank=True,null=True)












