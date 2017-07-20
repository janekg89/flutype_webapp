"""
Django models for the flutype webapp.
"""

# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import warnings

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User as DUser
from djchoices import DjangoChoices, ChoiceItem
from django.core.files.storage import FileSystemStorage
import pandas as pd
from flutype_analysis import analysis


fs = FileSystemStorage(location='../media')


class User(models.Model):
    """
    User model
    """
    # FIXME: use the django user model: see https://docs.djangoproject.com/en/1.11/topics/auth/
    name = models.CharField(max_length=50)

class PeptideType(DjangoChoices):
    """
    peptide type model
    """
    #p_types = models.CharField(max_length=30)
    peptide = ChoiceItem("PEP")
    buffer = ChoiceItem("BUF")
    empty = ChoiceItem("EMP")
    refrence = ChoiceItem("REF")
    antibody =ChoiceItem("AB")


class Buffer(DjangoChoices):
    """
    buffer model
    """
    #name = models.CharField(max_length=50)
    na = ChoiceItem("NA")
    pbst = ChoiceItem("PBST")
    natriumhydrogencarbonat = ChoiceItem("Natriumhydrogencarbonat")

class Substance(DjangoChoices):
    """
    substance model
    """
    #name = models.CharField(max_length=50,blank=True,null=True)
    nhs_3d=ChoiceItem("3D-NHS")

class HolderType(DjangoChoices):
    """
    holder type model
    """
    #holder_type=models.CharField(max_length=30,blank=True,null=True)

    microarray = ChoiceItem("microarray")
    microwell = ChoiceItem("microwell")

class Manufacturer(DjangoChoices):
    """
    manufacturer model
    """
    #name = models.CharField(max_length=30, null=True , blank=True)
    polyan= ChoiceItem("PolyAn")


class ProcessingType(DjangoChoices):
    substract_buffer= ChoiceItem("sub_buf")


class Peptide(models.Model):
    """
    Pepide model
    """
    sid= models.CharField(max_length=15, null=True)
    linker = models.CharField(max_length=50, blank=True, null=True)
    spacer = models.CharField(max_length=50, blank=True, null=True)
    sequence = models.CharField(max_length=50, blank=True, null=True)
    c_terminus = models.CharField(max_length=50, blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    pep_type = models.CharField(max_length=5,choices=PeptideType.choices, blank=True, null=True)
    comment = models.TextField(blank=True, null=True)


class Virus(models.Model):
    """
    virus model

    sid is the taxonomy id
    """
    sid = models.CharField(max_length=15, blank=True, null=True)
    subgroup = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    date_of_appearance = models.CharField(max_length=10, blank=True, null=True)
    strain = models.CharField(max_length=50, blank=True, null=True)

class Batch(models.Model):
    """
    Batch model as abstract class not stored in the database
    """
    concentration = models.FloatField(validators=[MinValueValidator(0)],
                                      blank=True, null=True)
    buffer = models.CharField(max_length=20,choices=Buffer.choices, blank=True, null=True)
    ph = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(14)],
                           blank=True, null=True)
    purity = models.FloatField(validators=[MinValueValidator(0)],
                               blank=True, null=True)
    produced_by = models.ForeignKey(User, blank=True, null=True)
    production_date = models.DateField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    class Meta:
        abstract = True


class VirusBatch(Batch):
    """
    Virus batch model
    """
    sid = models.CharField(max_length=20, blank=True, null=True)
    virus = models.ForeignKey(Virus,blank=True, null=True)
    passage_history = models.CharField(max_length=50, blank= True ,null=True)
    active = models.NullBooleanField(blank=True, null=True)
    labeling = models.CharField(max_length=50, blank=True,null=True)


class PeptideBatch(Batch):
    """
    peptide batch model
    """
    sid = models.CharField(max_length=20)
    peptide = models.ForeignKey(Peptide, blank=True, null=True)




##########################################################


class Treatment(models.Model):
    sid = models.CharField(max_length=10,null=True, blank=True)
    method = models.CharField(max_length=50, null=True, blank=True)
    order = models.IntegerField(blank=True, null=True)
    date_time = models.DateTimeField(null=True, blank=True)
    user = models.ForeignKey(User, null=True, blank=True)
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
    """ Spotting method and media related to spotting. """
    order = models.IntegerField(default=0, blank=True, null=True)


class Incubating(Treatment):
    duration = models.DurationField(null=True, blank=True)


class Quenching(Treatment):
    duration = models.DurationField(null=True, blank=True)
    substance = models.CharField(max_length=50, null=True, blank=True)

# TODO: list view (with links to RawCollections)
class Process(models.Model):
    washing = models.ForeignKey(Washing,null=True, blank=True)
    drying = models.ForeignKey(Drying,null=True, blank=True)
    spotting = models.ForeignKey(Spotting,null=True, blank=True)
    incubating = models.ForeignKey(Incubating,null=True, blank=True)
    quenching = models.ForeignKey(Quenching,null=True, blank=True)

######################################################################
class GalVirus(models.Model):
    sid = models.CharField(max_length=20)
    gal_file = models.FileField(upload_to="gal_vir",null=True, blank=True)

class GalPeptide(models.Model):
    sid = models.CharField(max_length=20)
    gal_file = models.FileField(upload_to="gal_pep", null=True, blank=True)


# TODO: view (list view & individual/detail entry)
class RawSpotCollection(models.Model):
    """
    A collection of raw spots: Information for a Collection of Spots collected at once for one microarray, one microwellplate
    """
    sid = models.CharField(max_length=20)
    batch = models.CharField(max_length=20, null=True, blank=True)
    holder_type = models.CharField(max_length=20, choices=HolderType.choices)
    functionalization = models.CharField(max_length=20,choices=Substance.choices)
    manufacturer = models.CharField(max_length=20,choices=Manufacturer.choices)
    image = models.ImageField(upload_to="scan",null=True, blank=True)
    gal_virus = models.ForeignKey(GalVirus,null=True, blank=True)
    gal_peptide = models.ForeignKey(GalPeptide,null=True, blank=True)
    process = models.ForeignKey(Process,blank=True, null=True)

    def peptide_set(self):
        """

        :return: a set of peptides which were used in RawSpotCollection
        """
        raw_spots = self.rawspot_set.all()
        unique_peptide_sid = []
        unique_peptide = []

        for raw_spot in raw_spots:
            if raw_spot.peptide_batch.peptide.sid in unique_peptide_sid:
                pass
            else:
                unique_peptide_sid.append(raw_spot.peptide_batch.peptide.sid)
                unique_peptide.append(raw_spot.peptide_batch.peptide)


        return unique_peptide

    def virus_set(self):
        """
        :return: a set of viruses which were used in RawSpotCollection
        """
        raw_spots = self.rawspot_set.all()
        unique_virus_sid = []
        unique_virus = []

        for raw_spot in raw_spots:
            virus = raw_spot.virus_batch.virus
            if not hasattr(virus, 'sid'):
                warnings.warn("No connection between peptide and peptide batch for virus: {}".format(virus))
            else:
                if virus.sid in unique_virus_sid:
                    pass
                else:
                    unique_virus_sid.append(raw_spot.virus_batch.virus.sid)
                    unique_virus.append(raw_spot.virus_batch.virus)


        return unique_virus


    def analysis(self):
        """ Returns the analysis object."""
        d = {'data_id': self.sid}
        d['gal_vir'] = pd.read_csv("../" + self.gal_virus.gal_file.url, sep='\t', index_col="ID")
        d['gal_pep'] = pd.read_csv("../" + self.gal_peptide.gal_file.url, sep='\t', index_col="ID")
        d['meta'] = "not necessary anymore"
        ana = analysis.Analysis(d)
        return ana


class SpotCollection(models.Model):
    raw_spot_collection = models.ForeignKey(RawSpotCollection)
    image2numeric_version = models.FloatField(default=0.1)
    processing_type = models.CharField(max_length=30,
                                       choices=ProcessingType.choices,
                                       blank=True,
                                       null=True)
    comment= models.TextField(default="The Intesity values are calcualted as the total intensity over a spot containing square."
                                      " The data is not preprocessed.")



# FIXME: it must be easy to get for one RawCollection entry all SpotCollections
# which belong to the RawCollection


    #raw_spots = models.ManyToManyField(RawSpot,through='Grid')
class RawSpot(models.Model):
    """
    spot model
    """
    peptide_batch = models.ForeignKey(PeptideBatch)
    virus_batch = models.ForeignKey(VirusBatch)
    raw_spot_collection = models.ForeignKey(RawSpotCollection)
    column = models.IntegerField()
    row = models.IntegerField()
    replica = models.IntegerField(null=True, blank=True)


    class Meta:
        unique_together = ('column', 'row', 'raw_spot_collection')


class Spot(models.Model):
    """
    spot model
    """
    raw_spot = models.ForeignKey(RawSpot)
    ############in results#########################
    intensity = models.FloatField(null=True, blank=True)
    std = models.FloatField(null=True, blank=True)
    spot_collection = models.ForeignKey(SpotCollection)






