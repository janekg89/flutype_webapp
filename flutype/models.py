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


"""
class User(models.Model):
    name = models.CharField(max_length=50)

class Peptide(models.Model):
    name = models.CharField(max_length=50,blank=True)
    linker = models.CharField(max_length=50,blank=True)
    spacer = models.CharField(max_length=50,blank=True)
    sequence = models.CharField(max_length=50,blank=True)
    c_terminus = models.CharField(max_length=50,blank=True)

    ####### there is probably better way, one of these has to be True########
    #blank = models.BooleanField()
    #reference = models.BooleanField()
    #antibody = models.BooleanField()
    ##########################################################################
class Peptite_type(models.Model):
    p_types = models.CharField(max_length=30)

class Virus(models.Model):
    subgroup = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    date = models.DateField()
    strain = models.CharField(max_length=50)


class Buffer(models.Model):
    name = models.CharField(max_length=50)


class Substance(models.Model):
    name = models.CharField(max_length=50)
    concentration = models.FloatField(validators=[MinValueValidator(0)],
                                      blank=True)



class Batch(models.Model):
    concentration = models.FloatField(validators=[MinValueValidator(0)],
                                      blank=True)
    buffer = models.ForeignKey("Buffer", blank=True)
    pH = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(14)],
                            blank=True)
    purity = models.FloatField(validators=[MinValueValidator(0)],
                               blank=True)
    produced_by = models.ManyToManyField("User", blank=True)
    production_date = models.DateField(blank=True)
    comment = models.TextField(blank=True)



class Peptide_batch(models.Model):
    batch = models.OneToOneField("Batch")
    peptide = models.ForeignKey("Peptide")

class Virus_batch(Batch):
    virus = models.ForeignKey("Virus")
    passage_history = models.CharField(max_length=50)
    active = models.BooleanField(blank=True)
    labeling = models.CharField(max_length=50,blank=True)












