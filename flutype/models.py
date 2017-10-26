# -*- coding: utf-8 -*-
"""
Django models for the flutype webapp.
"""
from __future__ import absolute_import, print_function, unicode_literals

import os
from django.core.validators import MaxValueValidator, MinValueValidator
from djchoices import DjangoChoices, ChoiceItem
from django.core.files.storage import FileSystemStorage
from django_pandas.io import read_frame
from flutype_webapp.settings import MEDIA_ROOT
from django.db import models
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
# FIXME: rename to BufferType
class Buffer(DjangoChoices):
    """ Buffer model. """
    na = ChoiceItem("NA")
    pbst = ChoiceItem("PBST")
    natriumhydrogencarbonat = ChoiceItem("Natriumhydrogencarbonat")


# FIXME: rename to FunctionalizationType (this is not a substance, but functionalization)
class Substance(DjangoChoices):
    """ Substance types. """
    nhs_3d = ChoiceItem("3D-NHS")
    no = ChoiceItem("No")
    epoxy_3d = ChoiceItem("3D-Epoxy")


class MeasurementType(DjangoChoices):
    """ Measurement types. """
    microarray = ChoiceItem("microarray")
    microwell = ChoiceItem("microwell")
    elisa = ChoiceItem("elisa")


class GalType(DjangoChoices):
    """ Type of gal file. """
    std = ChoiceItem("std")
    intensity = ChoiceItem("intensity")
    ligand_batch = ChoiceItem("ligand_batch")

# FIXME: rename to ManufacturerModel
class Manufacturer(DjangoChoices):
    """ Manufacturer type """
    polyan = ChoiceItem("PolyAn")


class ProcessingType(DjangoChoices):
    # FIXME: rename to substract_buffer (this does not save anything, be specific with the names)
    substract_buffer = ChoiceItem("sub_buf")


########################################
# Ligand
########################################
class Ligand(PolymorphicModel):
    """ Generic ligand.
    E.g, a peptide, virus or antibody.
    """
    sid = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
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


class Virus(Ligand):
    """ Virus ligand. """
    tax_id = models.CharField(max_length=CHAR_MAX_LENGTH, null=True)
    link_db = models.URLField(blank=True, null=True)
    subtype = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    isolation_country = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    collection_date = models.CharField(max_length=10, blank=True, null=True)
    strain = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    objects = LigandManager()


class Antibody(Ligand):
    """ Antibody ligand. """
    target = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    name = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    link_db = models.URLField(blank=True, null=True)
    objects = LigandManager()


class Complex(Ligand):
    """ Complex ligand. """
    complex_ligands = models.ManyToManyField(Ligand, related_name="complex_ligands")
    objects = ComplexManager()

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
    concentration = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True)
    buffer = models.CharField(max_length=CHAR_MAX_LENGTH, choices=Buffer.choices, blank=True, null=True)
    ph = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(14)], blank=True, null=True)
    purity = models.FloatField(validators=[MinValueValidator(0)], blank=True, null=True)
    produced_by = models.ForeignKey(User, blank=True, null=True)
    production_date = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.sid


class LigandBatch(Batch):
    """ Generic batch of a given ligand.
    This can be for instance a peptide, virus or antibody.
    """
    ligand = models.ForeignKey(Ligand, blank=True, null=True)
    objects = LigandBatchManager()


class VirusBatch(LigandBatch):
    """ Virus batch model. """
    passage_history = models.CharField(max_length=CHAR_MAX_LENGTH, blank=True, null=True)
    active = models.NullBooleanField(blank=True, null=True)
    objects = LigandBatchManager()


class PeptideBatch(LigandBatch):
    """ Peptide batch model. """
    objects = LigandBatchManager()


class AntibodyBatch(LigandBatch):
    """ Antibody batch model. """
    objects = LigandBatchManager()


class ComplexBatch(LigandBatch):
    """ Complex batch model. """
    objects = LigandBatchManager()


class BufferBatch(LigandBatch):
    """ Buffer batch model. """
    objects = LigandBatchManager()


########################################
# Gal files
########################################
class GalFile(Sidable, models.Model):
    type = models.CharField(max_length=CHAR_MAX_LENGTH, choices=GalType.choices)
    file = models.FileField(upload_to="gal_file", null=True, blank=True, storage=OverwriteStorage())
    objects = GalFileManager()

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
    temperature = models.CharField(max_length=300, null=True, blank=True)

    @property
    def get_step_type(self):
        """ Type of step."""
        subclass_object = Step.objects.get_subclass(id=self.id)
        return subclass_object

    def __str__(self):
        return self.sid


class Washing(Step):
    """ Washing step. """
    substance = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    objects = StepManager()


class Blocking(Step):
    """ Blocking step. """
    substance = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    objects = StepManager()


class Scanning(Step):
    """ Scanning step. """
    objects = StepManager()


class Drying(Step):
    """ Drying step. """
    substance = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    objects = StepManager()


class Spotting(Step):
    """ Spotting method and media related to spotting. """
    objects = StepManager()


class Incubating(Step):
    """ Incubating step. """
    duration = models.DurationField(null=True, blank=True)
    substance = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    objects = StepManager()

# FIXME: rename to IncubatingAnalyte
class IncubatingAnalyt(Step):
    """ Incubating analyte step. """
    duration = models.DurationField(null=True, blank=True)
    objects = StepManager()


class Quenching(Step):
    """ Quenching step. """
    duration = models.DurationField(null=True, blank=True)
    substance = models.CharField(max_length=CHAR_MAX_LENGTH, null=True, blank=True)
    objects = StepManager()


class ProcessStep(Userable, Commentable, Hashable, models.Model):
    """ Step in a process.
        Via the ProcessStep the Steps are connected to the process, thereby creating an order of the steps.
        This is the through model connecting steps with processes.

        index: position of step in the process.

    """
    process = models.ForeignKey(Process)
    step = models.ForeignKey(Step)
    raw_spot_collection =  models.ForeignKey(RawSpotCollection)

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


class Process(Sidable, models.Model):
    """ A process is a collection of process steps. """
    steps = models.ManyToManyField(Step, through='ProcessStep')
    unique_ordering = models.CharField(max_length=CHAR_MAX_LENGTH)
    objects = ProcessManager()

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


########################################
# Study
########################################
class Study(Commentable, Sidable, Dateable, Userable, Statusable, FileAttachable, Hidable, models.Model):
    """ Study is a collection of measurements.
    The top class for representation of experimental data.
    """
    description = models.TextField(blank=True, null=True)
    objects = StudyManager()

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
    functionalization = models.CharField(max_length=CHAR_MAX_LENGTH, choices=Substance.choices)
    manufacturer = models.CharField(max_length=CHAR_MAX_LENGTH, choices=Manufacturer.choices)
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
    column = models.IntegerField()
    row = models.IntegerField()
    objects = RawSpotManager()

    class Meta:
        unique_together = ('column', 'row', 'raw_spot_collection')

    def __str__(self):
        return str("column:"+str(self.column)+"-"+"row:"+str(self.row))


#####################################
# Quantified spots
#####################################
class SpotCollection(Sidable, Commentable, FileAttachable, models.Model):
    """ SpotCollection model. """
    raw_spot_collection = models.ForeignKey(RawSpotCollection)
    std_gal = models.ForeignKey(GalFile,null=True, blank=True,related_name="std_gal")
    int_gal = models.ForeignKey(GalFile,null=True, blank=True,related_name="int_gal")

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


class Spot(models.Model):
    """ Spot model. """
    raw_spot = models.ForeignKey(RawSpot)
    intensity = models.FloatField(null=True, blank=True)
    std = models.FloatField(null=True, blank=True)
    spot_collection = models.ForeignKey(SpotCollection)

    class Meta:
        unique_together = ('raw_spot', 'spot_collection')

    def __str__(self):
        # FIXME: create via a join of the parts
        return str("column:"+str(self.raw_spot.column)+"-"+"row:"+str(self.raw_spot.row)+"-"+"intensity:"+str(self.intensity))
