from __future__ import absolute_import, print_function, unicode_literals
from django.db import models
from django.apps import apps
from django.core.files import File


from flutype.helper import get_ligand_or_none, get_user_or_none, get_duration_or_none,\
    get_or_create_raw_doc, unique_ordering, read_tsv_table, get_unique_galfile,\
    create_spots, get_or_create_raw_spots

from polymorphic.manager import PolymorphicManager
import pandas as pd
import re
import os


try:
   unicode = unicode
except NameError:
   # 'unicode' is undefined, must be Python 3
   str = str
   unicode = str
   bytes = bytes
   basestring = (str,bytes)
else:
   # 'unicode' exists, must be Python 2
   str = str
   unicode = unicode
   bytes = str
   basestring = basestring


class LigandBatchManager(models.Manager):
    def get_or_create(self, *args, **kwargs):
        if "ligand" in kwargs and isinstance(kwargs['ligand'], basestring):
            kwargs['ligand'] =  get_ligand_or_none(kwargs['ligand'])
        if "produced_by" in kwargs and isinstance(kwargs['produced_by'], basestring):
            kwargs['produced_by'] =  get_user_or_none(kwargs['produced_by'])
        object, created = super(LigandBatchManager, self).get_or_create(*args,**kwargs)
        return object, created

class ComplexManager(PolymorphicManager):
    def get_or_create(self, *args, **kwargs):
        if "complex_ligands" in kwargs and isinstance(kwargs['complex_ligands'], basestring):
            complex_ligands = kwargs["complex_ligands"]
            del kwargs["complex_ligands"]
            object, created = super(ComplexManager,self).get_or_create(*args,**kwargs)
            for ligand_sid in complex_ligands.split('-'):
                ligand = get_ligand_or_none(ligand_sid)
                object.complex_ligands.add(ligand)
        else:
            object, created = super(ComplexManager,self).get_or_create(*args,**kwargs)

        return object, created

class StepManager(models.Manager):
    def get_or_create(self, *args, **kwargs):
        if "duration" in kwargs and isinstance(kwargs['duration'], basestring):
            kwargs["duration"]=get_duration_or_none(kwargs['duration'])
        object, created = super(StepManager, self).get_or_create(*args,**kwargs)
        return object, created




class StudyManager(models.Manager):
    def get_or_create(self, *args, **kwargs):
        if "sid" in kwargs:
            object, created = super(StudyManager, self).get_or_create(*args, **kwargs)

        if "meta" in kwargs:
            meta = kwargs["meta"]
            object, created = super(StudyManager, self).get_or_create(*args, **meta)

        if "raw_docs_fpaths" in kwargs:
            for fpath in kwargs["raw_docs_fpaths"]:
                raw_doc , _ = get_or_create_raw_doc(fpath=fpath)
                object.files.add(raw_doc)

        if "measurements" in kwargs:
            for measurement in kwargs["measurements"]:
                measurement_dic = kwargs["measurements"][measurement]
                measurement_dic["meta"]["study"] = object
                RawSpotCollection = apps.get_model("flutype", model_name="RawSpotCollection")
                measurement, created = RawSpotCollection.objects.get_or_create(**measurement_dic)


        return object, created


class MeasurementManager(models.Manager):
    def get_or_create(self, *args, **kwargs):

        if "sid" in kwargs:
            object, created = super(MeasurementManager, self).get_or_create(*args, **kwargs)

        if "meta" in kwargs:
            meta = kwargs["meta"]
            object, created = super(MeasurementManager, self).get_or_create(*args, **meta)

        if "raw_docs_fpaths" in kwargs:
            for fpath in kwargs["raw_docs_fpaths"]:
                raw_doc , _ = get_or_create_raw_doc(fpath=fpath)
                object.files.add(raw_doc)

        if "lig_mob_path" in kwargs:
            Galfile = apps.get_model("flutype", model_name="Galfile")
            lig_mob, created_m = Galfile.objects.get_or_create(lig_path=kwargs["lig_mob_path"])
            object.lig_mob = lig_mob
            lig_fix, created_l = Galfile.objects.get_or_create(lig_path=kwargs["lig_fix_path"])
            object.lig_fix =lig_fix
            kwargs["raw_spot_collection"]=object
            _ = get_or_create_raw_spots(**kwargs)



        if "steps_path" in kwargs:
            if kwargs["steps_path"]!= None:
                kwargs["raw_spot_collection"]= object
                Process = apps.get_model("flutype", model_name="Process")
                Process.objects.get_or_create(**kwargs)

        if "results" in kwargs:
            for result in kwargs["results"]:
                results_dic = kwargs["results"][result]
                results_dic["meta"]["raw_spot_collection"]= object
                Spotcollection = apps.get_model("flutype", model_name="Spotcollection")
                spotcollection, created = Spotcollection.objects.get_or_create(**results_dic)

        return object, created

class ProcessManager(models.Manager):

    def get_or_create(self,*args,**kwargs):

        intensity_path = kwargs["steps_path"]
        steps = read_tsv_table(intensity_path)
        raw_spot_collection = kwargs["raw_spot_collection"]



        kwargs = {"sid": unique_ordering(steps)}
        object, created = super(ProcessManager, self).get_or_create(*args, **kwargs)
        steps["start"]=steps["start"].str.replace('.', '-')
        for _ , step in steps.iterrows():

            Step= apps.get_model("flutype","Step")
            step_object = Step.objects.get(sid=step["step"])
            ProcessStep = apps.get_model("flutype","ProcessStep")
            process_step_object , _ = ProcessStep.objects.get_or_create(step=step_object,
                                                                        index=step["index"],
                                                                        start=step["start"],
                                                                        comment = step["comment"],
                                                                        raw_spot_collection=raw_spot_collection,
                                                                        process=object
                                                                        )
            if step["intensities"] is not None:
                intensity_fpath = os.path.join(os.path.dirname(intensity_path),step["intensities"])
                intensities_path_dic = {"intensities" :intensity_fpath}
                GalFile = apps.get_model("flutype", "GalFile")
                object_gal_file, _ = GalFile.objects.get_or_create(**intensities_path_dic)
                process_step_object.intensities =object_gal_file






        return object, created



class GalFileManager(models.Manager):

    def get_or_create(self,*args, **kwargs):
        if "sid" in kwargs:
            object, created = super(GalFileManager, self).get_or_create(*args, **kwargs)
            return object, created

        if "lig_path" in kwargs:
            kwargs["path"]= kwargs["lig_path"]
            object, max_name = get_unique_galfile( "gal_lig_", **kwargs)
            if object is None:
                sid = "gal_lig_{:03}".format(max_name + 1)
                meta = {"sid":sid}
                object, _ = super(GalFileManager, self).get_or_create(**meta)
                with open(kwargs["lig_path"]) as f:
                    object.file.save("{}.txt".format(object.sid), File(f))
                return object, True
            else:
                return object, False

        if "intensities" in kwargs and kwargs["intensities"] is not None:
            kwargs["path"]= kwargs["intensities"]

            object, max_name = get_unique_galfile("intensities_", **kwargs)
            if object is None:
                sid = "intensity_{:03}".format(max_name + 1)
                meta = {"sid": sid}
                object, _ = super(GalFileManager, self).get_or_create(**meta)
                with open(kwargs["intensities"]) as f:
                    object.file.save("{}.txt".format(object.sid), File(f))
                return object, True
            else:
                return object, False

        elif "std" in kwargs and kwargs["std"] is not None:
            kwargs["path"]=kwargs["std"]
            object, max_name = get_unique_galfile("std_", **kwargs)
            if object is None:
                    sid = "std_{:03}".format(max_name + 1)
                    meta = {"sid": sid}
                    object, _ = super(GalFileManager, self).get_or_create(**meta)
                    with open(kwargs["intensities"]) as f:
                        object.file.save("{}.txt".format(object.sid), File(f))
                    return object, True
            else:
                return object, False





class SpotcollectionManager(models.Manager):
    def get_or_create(self, *args, **kwargs):

        if "sid" in kwargs:
            object, created = super(SpotcollectionManager, self).get_or_create(*args, **kwargs)

        if "meta" in kwargs:
            meta = kwargs["meta"]
            object, created = super(SpotcollectionManager, self).get_or_create(*args, **meta)

        if "raw_docs_fpaths" in kwargs:
            for fpath in kwargs["raw_docs_fpaths"]:
                raw_doc , _ = get_or_create_raw_doc(fpath=fpath)
                object.files.add(raw_doc)

        if "std" in kwargs or "intensities" in kwargs:
            kwargs["spot_collection"]=object
            GalFile = apps.get_model("flutype", "GalFile")
            object_gal_file, _ = GalFile.objects.get_or_create(**kwargs)
            object.int_gal = object_gal_file





        return object, created


class SpotManager(models.Manager):
    def get_or_create(self, *args, **kwargs):
        if "lig_fix_batch" in kwargs and isinstance(kwargs['lig_fix_batch'], basestring):
            LigandBatch = apps.get_model("flutype","LigandBatch")
            ligandobject, created_l = LigandBatch.objects.get(sid="lig_fix_batch")
            kwargs["lig_fix_batch"] = ligandobject
            return super(SpotManager, self).get_or_create(**kwargs)

        if "lig_mob_batch" in kwargs and isinstance(kwargs['lig_mob_batch'], basestring):
            LigandBatch = apps.get_model("flutype","LigandBatch")
            ligandobject, created_l = LigandBatch.objects.get(sid="lig_mob_batch")
            kwargs["lig_mob_batch"] = ligandobject
            return super(SpotManager, self).get_or_create(**kwargs)












