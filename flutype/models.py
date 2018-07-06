# -*- coding: utf-8 -*-
"""
Django models for the flutype webapp.
"""
from __future__ import absolute_import, print_function, unicode_literals

import os
import numpy as np
from django.core.validators import MaxValueValidator, MinValueValidator
from djchoices import DjangoChoices, ChoiceItem
from django.core.files.storage import FileSystemStorage
from django_pandas.io import read_frame
from flutype_webapp.settings import MEDIA_ROOT
from django_measurement.models import MeasurementField
from .helper import AbstractClassWithoutFieldsNamed as without
from django.db import models
from measurement.base import BidimensionalMeasure
from measurement.measures import Volume, Mass
from django.contrib.auth.models import User
from .behaviours import Statusable, Dateable, Sidable, Userable, Commentable, FileAttachable, Hidable, Hashable
from model_utils.managers import InheritanceManager
from polymorphic.models import PolymorphicModel
from imagekit.models import ImageSpecField
from imagekit.processors import Transpose, ResizeToFit, Adjust
from .helper import OverwriteStorage, CHAR_MAX_LENGTH
from .managers import LigandBatchManager, ComplexManager, StepManager, StudyManager, MeasurementManager, GalFileManager,\
    ProcessManager, SpotcollectionManager, RawSpotManager, RawDocManager, LigandManager

fs = FileSystemStorage(location=MEDIA_ROOT)

#############################################################
# Helper models, i.e., choices
#############################################################

import datetime
YEAR_CHOICES = []
for r in range(1900, (datetime.datetime.now().year+1)):
    YEAR_CHOICES.append((r,r))

class Concentration(BidimensionalMeasure):
    PRIMARY_DIMENSION = Mass
    REFERENCE_DIMENSION = Volume


class UnitsType(DjangoChoices):
    """
    kilogram__l = ChoiceItem("kilogram__l")
    milligram__l = ChoiceItem("milligram__l")
    microgram__l = ChoiceItem("microgram__l")
    """

    M = ChoiceItem("M (molar)")
    mM = ChoiceItem("mM (milimolar)")
    muM = ChoiceItem("µM (µmolar)")
    nM = ChoiceItem("nM (nanomolar)")
    mg_per_l = ChoiceItem("mg/L (miligram per liter)")
    mug_per_l = ChoiceItem("µg/L (µgram per liter)")
    ng_per_l = ChoiceItem("ng/L (nanogram per liter)")
    stock__1 = ChoiceItem("stock__1")



class FunctionalizationType(DjangoChoices):
    """ Substance types. """
    nhs_3d = ChoiceItem("3D-NHS")
    no = ChoiceItem("No")
    epoxy_3d = ChoiceItem("3D-Epoxy")

class MeasurementType(DjangoChoices):
    """ Measurement types. """
    microarray = ChoiceItem("microarray")
    microwell = ChoiceItem("microwell")
    elisa = ChoiceItem("elisa")
    na_activitiy = ChoiceItem("na_activitiy")


class GalType(DjangoChoices):
    """ Type of gal file. """
    std = ChoiceItem("std")
    intensity = ChoiceItem("intensity")
    ligand_batch = ChoiceItem("ligand_batch")
    circle_quality =ChoiceItem("circle_quality")
    circle =ChoiceItem("circle")
    square =ChoiceItem("square")



class ManufacturerModel(DjangoChoices):
    """ Manufacturer type """
    polyan = ChoiceItem("PolyAn")
    ThermoF96Maxisorp = ChoiceItem("Thermo F96 Maxisorp")


class ProcessingType(DjangoChoices):
    substract_buffer = ChoiceItem("substract_buffer")


class Buffer(Sidable, Commentable, models.Model):
    """ Buffer model """
    name = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)



    def __str__(self):
        return self.sid

    @classmethod
    def url(cls):


        return "buffers"

    @classmethod
    def get_form(cls):
        from .forms import BufferForm
        return BufferForm


########################################
# Ligand
########################################
class Ligand(PolymorphicModel):
    """ Generic ligand.
    E.g, a peptide, virus or antibody.
    """
    sid = models.CharField(max_length=CHAR_MAX_LENGTH, unique=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.sid


class Peptide(Ligand):
    """ Pepide ligand. """
    linker = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    spacer = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    sequence = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    c_terminus = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    objects = LigandManager()

    @classmethod
    def url(cls):
        return "peptides"

    @classmethod
    def get_form(cls):
        from .forms import PeptideForm
        return PeptideForm


class Virus(Ligand):
    """ Virus ligand. """
    tax_id = models.CharField(max_length=CHAR_MAX_LENGTH, null=True,blank=True, unique=True)
    link_db = models.URLField(blank=True, null=True)
    subtype = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    isolation_country = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    collection_date = models.IntegerField( choices=YEAR_CHOICES, blank=True, null=True)
    strain = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    objects = LigandManager()

    class Meta:
        verbose_name_plural = "viruses"

    @classmethod
    def url(cls):
        return "viruses"

    @classmethod
    def get_form(cls):
        from .forms import VirusForm
        return VirusForm

class Antibody(Ligand):
    """ Antibody ligand. """
    target = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    link_db = models.URLField(blank=True, null=True)
    objects = LigandManager()

    class Meta:
        verbose_name_plural = "antibodies"

    @classmethod
    def url(cls):
        return "antibodies"

    @classmethod
    def get_form(cls):
        from .forms import AntibodyForm
        return AntibodyForm


class Complex(Ligand):
    """ Complex ligand. """
    complex_ligands = models.ManyToManyField(Ligand, related_name="complex_ligands")
    objects = ComplexManager()

    class Meta:
        verbose_name_plural = "complexes"


    @classmethod
    def url(cls):
        return "complexes"

    @classmethod
    def get_form(cls):
        from .forms import ComplexForm
        return ComplexForm

    @property
    def ligands_str(self):
        ligands = self.complex_ligands.values_list('sid', flat=True)
        vals = '-'.join(ligands)
        return vals


########################################
# Batch
########################################
class Batch(Sidable, Commentable, models.Model):
    """
    Batch model as abstract class not stored in database.
    The various ligand batches inherit from this class.

    labeling:  This is labeling after the batch was finished, e.g., giving labeled antibody to virus batch.
                This also handles the flurofix (fluorescent peptides)

    """
    labeling = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    #concentration = MeasurementField(measurement_class=Concentration,validators=[MinValueValidator(0)], blank=True, null=True)
    concentration = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True)
    concentration_unit = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True, choices= UnitsType.choices)
    ph = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(14)], blank=True, null=True)
    purity = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True)
    buffer = models.ForeignKey(Buffer, blank=True, null=True)
    produced_by = models.ForeignKey(User, blank=True, null=True)
    production_date = models.DateField(blank=True, null=True)
    stock = models.BooleanField(default=False)

    class Meta:
        abstract = True
        verbose_name_plural = "batches"

    def __str__(self):
        return self.sid

    def __repr__(self):
        return self.sid

class LigandBatch(Batch):
    """ Generic batch of a given ligand.
    This can be for instance a peptide, virus or antibody.
    """
    ligand = models.ForeignKey(Ligand, blank=True ,null= True)
    objects = LigandBatchManager()

    class Meta:
        verbose_name_plural = "ligand batches"


class VirusBatch(LigandBatch):
    """ Virus batch model. """
    passage_history = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    active = models.NullBooleanField(blank=True, null=True)
    objects = LigandBatchManager()

    class Meta:
        verbose_name_plural = "virus batches"

    @classmethod
    def url(cls):
        return "virusbatches"

    @classmethod
    def get_form(cls):
        from .forms import VirusBatchForm
        return VirusBatchForm


class PeptideBatch(LigandBatch):
    """ Peptide batch model. """
    objects = LigandBatchManager()

    class Meta:
        verbose_name_plural = "peptide batches"

    @classmethod
    def url(cls):
        return "peptidebatches"

    @classmethod
    def get_form(cls):
        from .forms import PeptideBatchForm
        return PeptideBatchForm

class AntibodyBatch(LigandBatch):
    """ Antibody batch model. """
    objects = LigandBatchManager()

    class Meta:
        verbose_name_plural = "antibody batches"

    @classmethod
    def url(cls):
        return "antibodybatches"

    @classmethod
    def get_form(cls):
        from .forms import AntibodyBatchForm
        return AntibodyBatchForm

class ComplexBatch(LigandBatch):
    """ Complex batch model. """
    objects = LigandBatchManager()

    class Meta:
        verbose_name_plural = "complex batches"

    @classmethod
    def url(cls):
        return "complexbatches"

    @classmethod
    def get_form(cls):
        from .forms import ComplexBatchForm
        return ComplexBatchForm


class BufferBatch(LigandBatch):
    """ Buffer batch model. """
    objects = LigandBatchManager()

    class Meta:
        verbose_name_plural = "buffer batches"

    @classmethod
    def url(cls):
        return "bufferbatches"

    @classmethod
    def get_form(cls):
        from .forms import BufferBatchForm
        return BufferBatchForm


########################################
# Gal files
########################################
class GalFile(Sidable,Hashable, models.Model):
    name = models.CharField(max_length=CHAR_MAX_LENGTH)
    type = models.CharField(max_length=CHAR_MAX_LENGTH, choices=GalType.choices)
    file = models.FileField(upload_to="gal_file", null=True, blank=True, storage=OverwriteStorage())
    rows_in_tray = models.IntegerField(null=True,blank=True)
    columns_in_tray = models.IntegerField(null=True,blank=True)
    vertical_trays = models.IntegerField(null=True,blank=True)
    horizontal_trays = models.IntegerField(null=True,blank=True)
    identical_trays = models.NullBooleanField(blank=True, null=True)
    ligand_batches = models.ManyToManyField(LigandBatch, blank=True)



    objects = GalFileManager()

    def create_gal_file_base(self):
        tray_x = np.array(range(self.rows_in_tray))
        tray_y = np.array(range(self.columns_in_tray))

        space_between_trays_x = tray_x.max() / 2
        space_between_trays_y = tray_y.max() / 2

        matrix_x = np.array(tray_x)
        matrix_y = np.array(tray_y)

        for _ in range(self.horizontal_trays - 1):
            matrix_x = np.append(matrix_x, tray_x + matrix_x.max() + space_between_trays_x)

        for _ in range(self.vertical_trays - 1):
            matrix_y = np.append(matrix_y, tray_y + matrix_y.max() + space_between_trays_y)

        xx, yy = np.meshgrid(matrix_x, matrix_y)

        positions = np.vstack([xx.ravel(), yy.ravel()])

        return positions.T

    def create_tray_base(self):
        tray_x = np.array(range(self.rows_in_tray))
        tray_y = np.array(range(self.columns_in_tray))

        xx, yy = np.meshgrid(tray_x, tray_y)

        positions = np.vstack([xx.ravel(), yy.ravel()])

        return positions.T

    def __str__(self):
        return self.sid


########################################
# Process & Steps
########################################
class Step(Sidable, Commentable, models.Model):
    """ Steps in the process.

        index: number of steps which gives the order
    """
    objects = InheritanceManager()
    method = models.CharField(max_length=300, null=True, blank=True)
    temperature = models.FloatField(null=True, blank=True)

    @property
    def get_step_type(self):
        """ Type of step."""
        subclass_object = Step.objects.get_subclass(id=self.id)
        return subclass_object

    @classmethod
    def url(cls):
        return "steps"


    def __str__(self):
        return self.sid


class Washing(Step):
    """ Washing step. """
    substance = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    objects = StepManager()

    @classmethod
    def get_form(cls):
        from .forms import WashingForm
        return WashingForm


class Blocking(Step):
    """ Blocking step. """
    substance = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    objects = StepManager()

    @classmethod
    def get_form(cls):
        from .forms import BlockingForm
        return BlockingForm


class Scanning(Step):
    """ Scanning step. """
    objects = StepManager()

    @classmethod
    def get_form(cls):
        from .forms import ScanningForm
        return ScanningForm


class Drying(Step):
    """ Drying step. """
    substance = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    objects = StepManager()

    @classmethod
    def get_form(cls):
        from .forms import DryingForm
        return DryingForm


class Spotting(Step):
    """ Spotting method and media related to spotting. """
    objects = StepManager()

    @classmethod
    def get_form(cls):
        from .forms import SpottingForm
        return SpottingForm


class Incubating(Step):
    """ Incubating step. """
    duration = models.DurationField(null=True, blank=True)
    substance = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    objects = StepManager()

    @classmethod
    def get_form(cls):
        from .forms import IncubatingForm
        return IncubatingForm

# FIXME: rename to IncubatingAnalyte
class IncubatingAnalyt(Step):
    """ Incubating analyte step. """
    duration = models.DurationField(null=True, blank=True)
    objects = StepManager()

    @classmethod
    def get_form(cls):
        from .forms import IncubatingAnalytForm
        return IncubatingAnalytForm

class Quenching(Step):
    """ Quenching step. """
    duration = models.DurationField(null=True, blank=True)
    substance = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    objects = StepManager()

    @classmethod
    def get_form(cls):
        from .forms import QuenchingForm
        return QuenchingForm


class Process(Sidable, models.Model):
    """ A process is a collection of process steps. """
    steps = models.ManyToManyField(Step, through='ProcessStep')
    unique_ordering = models.CharField(max_length=CHAR_MAX_LENGTH)
    objects = ProcessManager()

    class Meta:
        verbose_name_plural = "processes"

    def users(self):
        user_ids = self.processstep_set.values_list("user", flat="True").distinct()
        return User.objects.filter(id__in=user_ids)

    def is_step_in_process(self):
        result = True
        if self.steps.all().count() == 0:
            result = False
        return result

    # FIXME: rename to create_sid, this is what the function is doing

    @property
    def get_unique_ordering2(self):
        # FIXME: does this work ?
        ordered_step_ids = self.processstep_set.order_by('index').values_list('step__sid', flat=True)
        return  '-'.join(ordered_step_ids)

    # FIXME: function for creating the sid belongs here, not in the import

    @property
    def name(self):
        ordered_step_methods = self.processstep_set.order_by('index').values_list('step__method', flat=True)
        # FIXME: filter necessary
        values = [item for item in ordered_step_methods if item is not None]
        return '; '.join(values)

    def __str__(self):
        return self.sid


class ProcessStep(Userable, Commentable, Hashable, models.Model):
    """ Step in a process.
        Via the ProcessStep the Steps are connected to the process, thereby creating an order of the steps.
        This is the through model connecting steps with processes.

        index: position of step in the process.

    """
    process = models.ForeignKey(Process)
    step = models.ForeignKey(Step)
    raw_spot_collection = models.ForeignKey("RawSpotCollection")

    index = models.IntegerField(blank=True, null=True)
    start = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(upload_to="image", null=True, blank=True, storage=OverwriteStorage())
    image_contrast = ImageSpecField(source='image',
                                    processors=[Adjust(contrast=124, brightness=126)]
                                    )
    image_90 = ImageSpecField(source='image',
                              processors=[Transpose(Transpose.ROTATE_90), ResizeToFit(700, 200)],
                              )
    image_90_big = ImageSpecField(source='image',
                                  processors=[Transpose(Transpose.ROTATE_90), ResizeToFit(2800, 880)],
                                  )

    intensities = models.ForeignKey(GalFile, null=True, blank=True)

    # FIXME: ? what are the image fields  and image information doing in this models, also why are the intensities here?
    # This does not belong in the process step

    class Meta:
        ordering = ['index']
        unique_together = ["raw_spot_collection", "process","step","index"]

    def __str__(self):
        return str(self.process.sid + "-" + self.step.sid + "-" + str(self.index))



########################################
# Study
########################################
class Study(Commentable, Sidable, Dateable, Userable, Statusable, FileAttachable, Hidable, models.Model):
    """ Study is a collection of measurements.
    The top class for representation of experimental data.
    """
    description = models.TextField(blank=True, null=True)
    objects = StudyManager()

    class Meta:
        verbose_name_plural = "studies"

    @classmethod
    def url(cls):
        return "index"

    @classmethod
    def get_form(cls):
        from .forms import StudyForm
        return StudyForm

    def users(self):
        user_ids = self.rawspotcollection_set.values_list("processstep__user", flat="True").distinct()
        return User.objects.filter(id__in=user_ids)




########################################
# Measurement
########################################
# FIXME: why is studies on measurement, instead of of study having "measurements" ?
# This does make more sense for me (does not change much but is more logical, i.e. a Study has measurements.
# FIXME: change batch_id -> batch_number (this is not an sid in the data model, but the number of the batch)
class Measurement(Sidable, Commentable, Userable, FileAttachable, Hidable, models.Model):
    """ Measurement is a single experimental measurement. """
    measurement_type = models.CharField(max_length=CHAR_MAX_LENGTH, choices=MeasurementType.choices)
    batch_sid = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    functionalization = models.CharField(max_length=CHAR_MAX_LENGTH, choices=FunctionalizationType.choices)
    manufacturer = models.CharField(max_length=CHAR_MAX_LENGTH, choices=ManufacturerModel.choices)
    process = models.ForeignKey("Process", blank=True, null=True)
    studies = models.ManyToManyField(Study, blank=True)
    objects = MeasurementManager()

    def __str__(self):
        return self.sid

    class Meta:
        abstract = True


########################################
# Raw documents
########################################
class RawDoc(Sidable, Hashable,  models.Model):
    """ Additional files for given study or measurement. """
    file = models.FileField(upload_to="raw_docs", storage=OverwriteStorage())
    objects = RawDocManager()


########################################
# Raw spots & collection
########################################
# FIXME: probably it makes more sense to have just multiple gal files here, with every gal file
# defining the respective ligands. I think here about the issues with the ELISA measurements
# Probably something like
#
'''
class GalInformation(models.Model):
    gal = models.ForeignKey(GalFile, null=True, blank=True)
    ligands = models.ForeignKey(GalFile, null=True, blank=True)
    type = ...
'''
# with type being something from 'mobile', 'fixed', ...
# Than a RawSpotCollection has just one to many GalInformations which can be the mobile part, fixed part.


class RawSpotCollection(Measurement):
    """
    A collection of raw spots: Information for a Collection of Spots collected at once for one microarray,
    one microwellplate
    """
    lig_fix = models.ForeignKey(GalFile, null=True, blank=True, related_name='lig_fix')
    lig_mob = models.ForeignKey(GalFile, null=True, blank=True, related_name='lig_mob')

    ligands1 = models.ManyToManyField(Ligand, related_name="ligands1")
    ligands2 = models.ManyToManyField(Ligand, related_name="ligands2")

    @property
    def is_picture_in_rsc(self):
        result = False
        for processstep in self.processstep_set.all():
            if processstep.image:
                result = True
        return result

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

    @classmethod
    def url(cls, *args):
        url = 'measurements'
        return url

    def is_spot_collection(self):
        result = True
        if self.spotcollection_set.all().count() == 0:
            result = False
        return result

    def pivot_ligand1(self):
        data = read_frame(self.rawspot_set.all(), fieldnames=["row", "column", "lig_fix_batch__ligand__sid"])
        lig1 = data.pivot(index="row", columns="column", values="lig_fix_batch__ligand__sid")
        lig1.fillna(value="", inplace=True)
        return lig1


    def pivot_ligand2(self):
        try:
            data = read_frame(self.rawspot_set.all(), fieldnames=["row", "column", "lig_mob_batch__ligand__virus__subtype"])
            lig2 = data.pivot(index="row", columns="column", values="lig_mob_batch__ligand__virus__subtype")
        except:
            data = read_frame(self.rawspot_set.all(), fieldnames=["row", "column", "lig_mob_batch__ligand__sid"])
            lig2 = data.pivot(index="row", columns="column", values="lig_mob_batch__ligand__sid")
        lig2.fillna(value="", inplace=True)
        return lig2

    def pivot_concentration1(self):
        data = read_frame(self.rawspot_set.all(), fieldnames=["row", "column", "lig_fix_batch__concentration"])
        concentration = data.pivot(index="row", columns="column", values="lig_fix_batch__concentration")
        concentration.fillna(value="", inplace=True)
        return concentration

    def pivot_concentration2(self):
        data = read_frame(self.rawspot_set.all(), fieldnames=["row", "column", "lig_mob_batch__concentration"])
        concentration = data.pivot(index="row", columns="column", values="lig_mob_batch__concentration")
        concentration.fillna(value="", inplace=True)
        return concentration


class RawSpot(models.Model):
    """ Spot model. """
    raw_spot_collection = models.ForeignKey(RawSpotCollection)
    lig_fix_batch = models.ForeignKey(LigandBatch, related_name="lig_fix_batch", null=True, blank=True)
    lig_mob_batch = models.ForeignKey(LigandBatch, related_name="lig_mob_batch", null=True, blank=True)
    circle_quality =  models.FloatField(null=True, blank=True)
    column = models.IntegerField()
    row = models.IntegerField()
    objects = RawSpotManager()
    #to do Block

    class Meta:
        unique_together = ('column', 'row', 'raw_spot_collection')

    def __str__(self):
        return str("column:"+str(self.column)+"-"+"row:"+str(self.row))


#####################################
# Quantified spots
#####################################
class SpotCollection(Commentable, FileAttachable, models.Model):
    """ SpotCollection model. """
    sid = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    raw_spot_collection = models.ForeignKey(RawSpotCollection)
    std_gal = models.ForeignKey(GalFile,null=True, blank=True,related_name="std_gal")
    int_gal = models.ForeignKey(GalFile,null=True, blank=True,related_name="int_gal")
    square_gal = models.ForeignKey(GalFile,null=True, blank=True,related_name="square_gal")
    circle_gal = models.ForeignKey(GalFile,null=True, blank=True,related_name="circle_gal")
    circle_q_gal = models.ForeignKey(GalFile,null=True, blank=True,related_name="circle_q_gal")
    image = models.ImageField(upload_to="image", null=True, blank=True, storage=OverwriteStorage())




    processing_type = models.CharField(max_length=CHAR_MAX_LENGTH,
                                       choices=ProcessingType.choices,
                                       blank=True,
                                       null=True)
    objects = SpotcollectionManager()

    def __str__(self):
        return str(self.raw_spot_collection.sid+"+"+self.sid)

    def pivot_intensity(self):
        data = read_frame(self.spot_set.all(), fieldnames=["raw_spot__row", "raw_spot__column", "intensity"])
        intensity = data.pivot(index="raw_spot__row", columns="raw_spot__column", values="intensity")
        intensity.fillna(value="", inplace=True)
        return intensity

    def pivot_std(self):
        data = read_frame(self.spot_set.all(), fieldnames=["raw_spot__row", "raw_spot__column", "std"])
        std = data.pivot(index="raw_spot__row", columns="raw_spot__column", values="std")
        std.fillna(value="", inplace=True)
        return std

    class Meta:
        unique_together = ('raw_spot_collection', 'sid')


class Circle(models.Model):
    x = models.FloatField()
    y = models.FloatField()
    radius = models.FloatField()

class Square(models.Model):
    x_left = models.FloatField()
    y_left = models.FloatField()
    x_right = models.FloatField()
    y_right = models.FloatField()


class Spot(models.Model):
    """ Spot model. """
    intensity = models.FloatField(null=True, blank=True)
    std = models.FloatField(null=True, blank=True)
    circle_quality = models.FloatField(null=True, blank=True)

    raw_spot = models.ForeignKey(RawSpot)
    circle = models.ForeignKey(Circle,null=True, blank=True)
    square = models.ForeignKey(Square,null=True, blank=True)

    spot_collection = models.ForeignKey(SpotCollection)

    class Meta:
        unique_together = ('raw_spot', 'spot_collection')

    def __str__(self):
        # FIXME: create via a join of the parts
        return str("column:"+str(self.raw_spot.column)+"-"+"row:"+str(self.raw_spot.row)+"-"+"intensity:"+str(self.intensity))

