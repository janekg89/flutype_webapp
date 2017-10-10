from __future__ import absolute_import, print_function, unicode_literals
from django.db import models
from django.apps import apps
from django.core.files import File


from flutype.helper import get_ligand_or_none, get_user_or_none, get_duration_or_none,\
    get_or_create_raw_doc, unique_ordering, read_tsv_table

from polymorphic.manager import PolymorphicManager
import pandas as pd
import re



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
                Measurement = apps.get_model("flutype", model_name="Measurement")
                measurement, created = Measurement.objects.get_or_create(**measurement_dic)


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
            lig_mob, created = Galfile.objects.get_or_create(lig_path=kwargs["lig_mob_path"])
            object.lig_mob = lig_mob
            lig_fix, created = Galfile.objects.get_or_create(lig_path=kwargs["lig_fix_path"])
            object.lig_fix =lig_fix

        if "steps_path" in kwargs:
            kwargs["raw_spot_collection"]= object
            Process = apps.get_model("flutype", model_name="Process")
            Process.objects.get_or_create(**kwargs)

        if "results" in kwargs:
            for result in kwargs["results"]:
                results_dic = kwargs["results"][result]
                results_dic["meta"]["raw_spot_collection"]= object
                #Spotcollection = apps.get_model("flutype", model_name="Spotcollection")
                #spotcollection, created = Spotcollection.objects.get_or_create(**results_dic)

        return object, created

class ProcessManager(models.Manager):

    def get_or_create(self,*args,**kwargs):

        steps = read_tsv_table(kwargs["steps_path"])
        raw_spot_collection = kwargs["raw_spot_collection"]



        kwargs = {"sid": unique_ordering(steps)}
        object, created = super(ProcessManager, self).get_or_create(*args, **kwargs)

        for step in steps:
            print(step)
            Step = apps.get_model("flutype","Step")

            ProcessStep = apps.get_model("flutype","ProcessStep")
            GalFile= apps.get_model("flutype","GalFile")
            object_gal_file, _ = GalFile.objects.get_or_create(step)

            ProcessStep.objects.get_or_create(step=step["step"],
                                              index=step["index"],
                                              start=step["start"],
                                              comment = step["comment"],
                                              intensities = object_gal_file,
                                              raw_spot_collection = raw_spot_collection)
            ProcessStep.intensities.save()




            step_object =Step.objects.get(sid=step)

        return object, created


class ProcessStepManager(models.Manager):
    def create(self, *args, **kwargs):
        pass

class GalFileManager(models.Manager):

    def get_or_create(self,*args, **kwargs):
        if "lig_path" in kwargs:
            GalFile = apps.get_model("flutype", model_name="GalFile")
            this_gal = pd.read_csv(kwargs["lig_path"], sep='\t', index_col="ID")
            max_name = 0
            for gal_file in GalFile.objects.all():

                result = re.search('gal_lig_(.*)', gal_file.sid)
                if int(result.group(1)) > max_name:
                    max_name = int(result.group(1))

                df_gal = pd.read_csv(gal_file.file.path, sep='\t', index_col="ID")
                if df_gal.equals(this_gal):
                    return gal_file , False

            object = super(GalFileManager, self).create(sid= "gal_lig_{:03}".format(max_name+1))
            object.file.save("{}.txt".format(object.sid), File(open(kwargs["lig_path"])))
            return object, True

        if "intensity" in kwargs:
            if kwargs["intensity"]:
                print("hi")








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

        if "std" in kwargs:
            pass


        elif "intensity" in kwargs:
            pass








        return object, created







