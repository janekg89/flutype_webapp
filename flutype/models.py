"""
Django models for the flutype webapp.
"""

# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

import os
import pandas as pd

from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User as DUser
from djchoices import DjangoChoices, ChoiceItem
from django.core.files.storage import FileSystemStorage

from django_pandas.io import read_frame
from flutype_webapp.settings import MEDIA_ROOT

fs = FileSystemStorage(location=MEDIA_ROOT)

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.contrib.auth.models import User
from model_utils.managers import InheritanceManager
from polymorphic.models import PolymorphicModel
from imagekit.models import ImageSpecField
from imagekit.processors import Transpose, ResizeToFit


CHAR_MAX_LENGTH = 50

class OverwriteStorage(FileSystemStorage):
    """
    Overwrite storage overwrites existing names by deleting the resources.
    ! Use with care. This deletes files from the media folder !
    """
    def get_available_name(self, name, **kwargs):
        if self.exists(name):
            os.remove(os.path.join(settings.MEDIA_ROOT, name))
        return name

#############################################################
# Helper models, i.e., choices
#############################################################

class Buffer(DjangoChoices):
    """
    buffer model
    """
    na = ChoiceItem("NA")
    pbst = ChoiceItem("PBST")
    natriumhydrogencarbonat = ChoiceItem("Natriumhydrogencarbonat")


class Substance(DjangoChoices):
    """
    substance model
    """
    nhs_3d=ChoiceItem("3D-NHS")


class ExperimentType(DjangoChoices):
    """
    holder type model
    """
    microarray = ChoiceItem("microarray")
    microwell = ChoiceItem("microwell")
    elisa = ChoiceItem("elisa")


class Manufacturer(DjangoChoices):
    """
    manufacturer model
    """
    polyan= ChoiceItem("PolyAn")


class ProcessingType(DjangoChoices):
    substract_buffer= ChoiceItem("sub_buf")


########################################
# Ligand
########################################

class Ligand(PolymorphicModel):
    """
    Generic ligand.
    This can be for instance a peptide, virus or antibody.
    """
    sid = models.CharField(max_length=CHAR_MAX_LENGTH, null=True)
    comment = models.TextField(blank=True, null=True)


class Peptide(Ligand):
    """
    Pepide ligand.
    """
    linker = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    spacer = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    sequence = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    c_terminus = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)


class Virus(Ligand):
    """
    Virus ligand
    """
    tax_id = models.CharField(max_length=CHAR_MAX_LENGTH, null=True)
    link_db = models.URLField(blank=True, null=True)
    # fludb_id
    subtype = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    isolation_country = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    collection_date = models.CharField(max_length=10, blank=True, null=True)
    strain = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)


class Antibody(Ligand):
    target = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    # FIXME: monoclonal/polyclonal
    link_db = models.URLField(blank=True, null=True)


# TODO: complex


########################################
# Batch
########################################

class Batch(models.Model):
    """
    Batch model as abstract class not stored in database.
    The various ligand batches inherit from this class.

    labeling:  This is labeling after the batch was finished, e.g., giving labeled antibody to virus batch.
                This also handles the flurofix (fluorescent peptides)

    """
    sid = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    labeling = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)

    concentration = models.FloatField(validators=[MinValueValidator(0)],
                                      blank=True, null=True)
    buffer = models.CharField(max_length=CHAR_MAX_LENGTH,choices=Buffer.choices, blank=True, null=True)
    ph = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(14)],
                           blank=True, null=True)
    purity = models.FloatField(validators=[MinValueValidator(0)],
                               blank=True, null=True)
    produced_by = models.ForeignKey(User, blank=True, null=True)
    production_date = models.DateField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True


class LigandBatch(Batch):
    """
    Generic batch of a given ligand.
    This can be for instance a peptide, virus or antibody.

        mobile: is the ligand immobilized on surface, or in solution (other options ?)
    """
    ligand = models.ForeignKey(Ligand, blank=True, null=True)
    mobile = models.NullBooleanField(blank=True, null=True)


class VirusBatch(LigandBatch):
    """
    Virus batch model
    """

    passage_history = models.CharField(max_length=CHAR_MAX_LENGTH, blank= True ,null=True)
    active = models.NullBooleanField(blank=True, null=True)



class PeptideBatch(LigandBatch):
    """
    peptide batch model
    """


class AntibodyBatch(LigandBatch):
    """
    peptide batch model
    """
    pass

########################################
# Process & Treatment
########################################
# The steps in the process.


class Step(models.Model):
    """
    Steps in the process.

        index: number of steps which gives the order
    """
    objects = InheritanceManager()
    sid = models.CharField(max_length=CHAR_MAX_LENGTH,null=True, blank=True)
    method = models.CharField(max_length=300, null=True, blank=True)
    temperature = models.CharField(max_length=300, null=True, blank=True)
    comment = models.TextField(blank=True, null=True)


    @property
    def get_step_type(self):
        """ Type of step."""
        subclass_object = Step.objects.get_subclass(id=self.id)
        return subclass_object


class Washing(Step):
    substance = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)


class Blocking(Step):
    substance = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)


class Scanning(Step):
    pass


class Drying(Step):
    substance = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)


class Spotting(Step):
    """ Spotting method and media related to spotting. """
    pass


class Incubating(Step):
    duration = models.DurationField(null=True, blank=True)


class Quenching(Step):
    duration = models.DurationField(null=True, blank=True)
    substance = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)


########################################
# Gal files
########################################
class GalFile(models.Model):
    sid = models.CharField(max_length=CHAR_MAX_LENGTH)
    file = models.FileField(upload_to="gal_file", null=True, blank=True, storage=OverwriteStorage())

# class GalVirus(models.Model):
#    sid = models.CharField(max_length=CHAR_MAX_LENGTH)
#    file = models.FileField(upload_to="gal_vir", null=True, blank=True, storage=OverwriteStorage())


# probably measurement ?
class Experiment(models.Model):
    """
    FIXME: an experiment can have multiple image/data files
    """

    sid = models.CharField(max_length=CHAR_MAX_LENGTH)
    experiment_type = models.CharField(max_length=CHAR_MAX_LENGTH, choices=ExperimentType.choices)
    batch = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    functionalization = models.CharField(max_length=CHAR_MAX_LENGTH, choices=Substance.choices)
    manufacturer = models.CharField(max_length=CHAR_MAX_LENGTH, choices=Manufacturer.choices)
    process = models.ForeignKey("Process", blank=True, null=True)
    comment = models.TextField(null=True, blank=True)


class Process(models.Model):
    """ A process is a collection of process steps.
    Every step has an index.

    """
    sid = models.CharField(max_length=CHAR_MAX_LENGTH)
    steps = models.ManyToManyField(Step, db_index=True, through='ProcessStep')


    def users(self):
        user_ids = self.processstep_set.values_list("user", flat="True").distinct()
        return User.objects.filter(id__in=user_ids)


    def is_step_in_process(self):
        result = True
        if self.steps.all().count() == 0:
            result = False
        return result

    @property
    def identical_ordering(self):
        """ Creates DataFrame from given steps.

        :return:
        """
        data = read_frame(self.processstep_set.all(), fieldnames=["process__sid", "index"])
        # TODO: sort step id by index, create string S1-S2-S3, use this string to compare
        return data

    # TODO: overwrite the save method on model to add uniqueness constraint


class ProcessStep(models.Model):
    """ Single step in an actual process.
        Connecting the Steps to the process, creating an order of the steps.

        index: position of step in the process.

    """
    process = models.ForeignKey(Process)
    step = models.ForeignKey(Step)
    index = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(User, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    finish = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    # FIXME: property all users involved in the process, i.e.
    # everybody involved in any step in the process

    class Meta:
        unique_together = ('process', 'step', 'index')
        ordering = ['index', ]


class RawSpotCollection(Experiment):
    """
    A collection of raw spots: Information for a Collection of Spots collected at once for one microarray, one microwellplate
    """
    image = models.ImageField(upload_to="image", null=True, blank=True, storage=OverwriteStorage())
    image_90 =  ImageSpecField(source='image',
                               processors=[Transpose(Transpose.ROTATE_90),ResizeToFit(350,100)],
                               )
    gal_file1 = models.ForeignKey(GalFile, null=True, blank=True, related_name='gal_file1')
    gal_file2 = models.ForeignKey(GalFile, null=True, blank=True, related_name='gal_file2')

    ligands1 = models.ManyToManyField(Ligand, related_name="ligands1")
    ligands2 = models.ManyToManyField(Ligand, related_name="ligands2")

    @property
    def viruses1(self):
        return self.ligands1.instance_of(Virus)

    @property
    def viruses2(self):
        return self.ligands2.instance_of(Virus)

    @property
    def antibodies1(self):
        return self.ligands1.instance_of(Antibody)

    @property
    def antibodies2(self):
        return self.ligands2.instance_of(Antibody)

    @property
    def peptides1(self):
        return self.ligands1.instance_of(Peptide)

    @property
    def peptides2(self):
        return self.ligands2.instance_of(Peptide)


    def is_spot_collection(self):
        result = True
        if self.spotcollection_set.all().count() == 0:
            result = False
        return result

    def pivot_ligand1(self):
        data = read_frame(self.rawspot_set.all(), fieldnames=["row","column","ligand1__ligand__sid"])
        lig1 = data.pivot(index="row", columns="column", values="ligand1__ligand__sid")
        lig1.fillna(value="", inplace=True)
        return lig1

    def pivot_ligand2(self):
        try:
            data = read_frame(self.rawspot_set.all(), fieldnames=["row","column","ligand2__ligand__virus__subtype"])
            lig2 = data.pivot(index="row", columns="column", values="ligand2__ligand__virus__subtype")
        except:
            data = read_frame(self.rawspot_set.all(), fieldnames=["row", "column", "ligand2__ligand__sid"])
            lig2 = data.pivot(index="row", columns="column", values="ligand2__ligand__sid")
        lig2.fillna(value="", inplace=True)
        return lig2

    def pivot_concentration1(self):
        data = read_frame(self.rawspot_set.all(), fieldnames=["row","column","ligand1__concentration"])
        concentration = data.pivot(index="row", columns="column", values="ligand1__concentration")
        concentration.fillna(value="", inplace=True)
        return concentration

    def pivot_concentration2(self):
        data = read_frame(self.rawspot_set.all(), fieldnames=["row","column","ligand2__concentration"])
        concentration = data.pivot(index="row", columns="column", values="ligand2__concentration")
        concentration.fillna(value="", inplace=True)
        return concentration


class RawSpot(models.Model):
    """
    spot model
    """
    raw_spot_collection = models.ForeignKey(RawSpotCollection)
    ligand1 = models.ForeignKey(LigandBatch, related_name="ligand1",null=True, blank=True)
    ligand2 = models.ForeignKey(LigandBatch, related_name="ligand2",null=True, blank=True)
    column = models.IntegerField()
    row = models.IntegerField()

    class Meta:
        unique_together = ('column', 'row', 'raw_spot_collection')


#####################################
# Quantified interaction strength
#####################################

class SpotCollection(models.Model):
    sid = models.CharField(max_length=CHAR_MAX_LENGTH)
    raw_spot_collection = models.ForeignKey(RawSpotCollection)
    image2numeric_version = models.FloatField(default=0.1)
    processing_type = models.CharField(max_length=CHAR_MAX_LENGTH,
                                       choices=ProcessingType.choices,
                                       blank=True,
                                       null=True)
    comment = models.TextField(default="A spot detecting script has located the spots in the image."
                                      "The spots are centered in a larger square."
                                      "The Intesity values are calculated as the total intensity over that square. "
                                      "The image is not preprocessed.")

# perhaps name Interaction
class Spot(models.Model):
    """
    spot model
    """
    raw_spot = models.ForeignKey(RawSpot)

    ############in results#########################
    intensity = models.FloatField(null=True, blank=True)
    std = models.FloatField(null=True, blank=True)
    spot_collection = models.ForeignKey(SpotCollection)
    #TODO: add Coordinates on image





