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
from django.db.utils import IntegrityError

from django_pandas.io import read_frame


from flutype_analysis import analysis
from flutype_webapp.settings import MEDIA_ROOT

fs = FileSystemStorage(location=MEDIA_ROOT)

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

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

class Ligand(models.Model):
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
    # FIXME: extend/change the virus model
    tax_id = models.CharField(max_length=CHAR_MAX_LENGTH, null=True)
    link_db = models.URLField()
    # fludb_id
    subtype = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    isolation_country = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    # FIXME: wrong, i.ei, date_of_collection
    collection_date = models.CharField(max_length=10, blank=True, null=True)
    strain = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)

class Antibody(Ligand):
    target = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    # FIXME: monoclonal/polyclonal
    link_db =  models.URLField()


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
    ligand = models.ForeignKey(Ligand)
    mobile = models.BooleanField()


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
    pass

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
    sid = models.CharField(max_length=CHAR_MAX_LENGTH,null=True, blank=True)
    method = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    index = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(User, null=True, blank=True)
    date_time = models.DateTimeField(null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    # FIXME: make steps index unique in process.



    def _get_step_type(self):
        """ Type of step."""
        return self.__class__.__name__

    step_type = property(_get_step_type)


class Washing(Step):
    substance = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)


class Drying(Step):
    substance = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)


class Spotting(Step):
    """ Spotting method and media related to spotting. """
    pas


class Incubating(Step):
    duration = models.DurationField(null=True, blank=True)


class Quenching(Step):
    duration = models.DurationField(null=True, blank=True)
    substance = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)


class Process(models.Model):
    """
        user: is the main user responsible for the experiment
    """
    sid = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    steps = models.ManyToManyField(Step, db_index=True)

    # washing = models.ForeignKey(Washing,null=True, blank=True)
    # drying = models.ForeignKey(Drying,null=True, blank=True)
    # spotting = models.ForeignKey(Spotting,null=True, blank=True)
    # incubating = models.ForeignKey(Incubating,null=True, blank=True)
    # quenching = models.ForeignKey(Quenching,null=True, blank=True)


    # TODO: check what is best solution to store user
    user = models.ForeignKey(User, null=True, blank=True)

    # FIXME: property all users involved in the process, i.e.
    # everybody involved in any step in the process
    def users(self):
        users = []
        for step in self.steps.all():
            users.append(step.user)
        return users




"""
@receiver(m2m_changed, sender=Process.steps.trough)
def verify_uniqueness(sender, **kwargs):
    index = kwargs.get("index", None)
    for step in steps:
"""



# TODO: find a clever solution to check if two processes are identical
# independet of user & date (requires consistency in data)
# Not sure if on model level or afterwards.


########################################
# Gal files
########################################
class GalFile(models.Model):
    sid = models.CharField(max_length=CHAR_MAX_LENGTH)
    file = models.FileField(upload_to="gal_lig", null=True, blank=True, storage=OverwriteStorage())

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
    process = models.ForeignKey(Process, blank=True, null=True)
    comment = models.TextField(null=True, blank=True)

class Elisa(Experiment):
    pass


class RawSpotCollection(Experiment):
    """
    A collection of raw spots: Information for a Collection of Spots collected at once for one microarray, one microwellplate
    """
    image = models.ImageField(upload_to="image", null=True, blank=True, storage=OverwriteStorage())
    gal_file1 = models.ForeignKey(GalFile, null=True, blank=True, related_name='gal_file1')
    gal_file2 = models.ForeignKey(GalFile, null=True, blank=True, related_name='gal_file2')

    ligands1 = models.ManyToManyField(Ligand, related_name="ligands1")
    ligands2 = models.ManyToManyField(Ligand, related_name="ligands2")


    def viruses1(self):
        # TODO: filter by the ligand type
        return self.ligands1

    def viruses2(self):
        # TODO: filter by the ligand type
        return self.ligands2

    # TODO: also for peptides and antibodies


    def is_spot_collection(self):
        result = True
        if self.spotcollection_set.all().count() == 0:
            result = False
        return result

    # TODO: refactor analyis function
    def analysis(self):
        """ Returns the analysis object. """
        d = {'data_id': self.sid}

        row = []
        column = []
        pep_name = []
        vir_name = []
        for raw_spot in self.rawspot_set.all():
            row.append(raw_spot.row)
            column.append(raw_spot.column)
            pep_name.append(raw_spot.ligand.peptide_batch.sid)
            vir_name.append(raw_spot.virus_batch.sid)

        data = pd.DataFrame(row, columns=["Row"])
        data["Column"] = column
        pep_data = data.copy()
        vir_data = data.copy()

        pep_data["Name"] = pep_name
        vir_data["Name"] = vir_name

        d['gal_vir'] = vir_data.copy()
        d['gal_pep'] = pep_data.copy()
        ana = analysis.Analysis(d)

        return ana


class RawSpot(models.Model):
    """
    spot model
    """
    raw_spot_collection = models.ForeignKey(RawSpotCollection)
    ligand1 = models.ForeignKey(LigandBatch, related_name="ligand1")
    ligand2 = models.ForeignKey(LigandBatch, related_name="ligand2")
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

    def analysis(self):
        """ Returns the analysis object."""
        d = {'data_id': self.raw_spot_collection.sid}
        data = read_frame(self.spot_set.all(),fieldnames=["intensity"])
        raw = []
        column = []
        pep_name = []
        vir_name = []
        for spot in self.spot_set.all():
            raw.append(spot.raw_spot.row)
            column.append(spot.raw_spot.column)
            pep_name.append(spot.raw_spot.ligand.peptide_batch.sid)
            vir_name.append(spot.raw_spot.virus_batch.sid)

        data["Row"] = raw
        data["Column"] = column
        pep_data = data.copy()
        vir_data = data.copy()

        pep_data["Name"] = pep_name
        vir_data["Name"] = vir_name
        d["gal_vir"] = vir_data.copy()
        d["gal_pep"] = pep_data.copy()
        d["data"] = data.pivot(index="Row", columns="Column", values="intensity")
        ana = analysis.Analysis(d)

        return ana


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
    #TODO: add Coordinates on Image






