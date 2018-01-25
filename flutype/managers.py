from __future__ import absolute_import, print_function, unicode_literals
from django.db import models
from django.apps import apps
from django.core.files import File
from django_pandas.io import read_frame
from django.utils import timezone
import datetime
from .behaviours import Status
from model_utils.managers import InheritanceManager
from guardian.shortcuts import assign_perm



from flutype.helper import get_ligand_or_none, get_buffer_or_none,get_user_or_none, get_duration_or_none,\
    unique_ordering, read_tsv_table, get_unique_galfile,\
    create_spots, get_or_create_raw_spots, md5, read_gal_file, read_gal_file_to_temporaray_file, clean_step_table,\
    nan_to_none_in_pdtable

from polymorphic.manager import PolymorphicManager
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

class LigandManager(PolymorphicManager):

    def all_to_df(self):
        dic_ligand_batches = {}
        for batch in dic_ligand_batches:
            dic_ligand_batches[batch] = self.to_df()

    def to_df(self):
        df = read_frame(self.all())

    def get_or_create(self, *args, **kwargs):
        if "collection_date" in kwargs and isinstance(kwargs['collection_date'], basestring):
            kwargs['collection_date'] = int(kwargs['collection_date'])
        object, created = super(LigandManager, self).get_or_create(*args, **kwargs)
        return object, created



class LigandBatchManager(InheritanceManager):
    def get_or_create(self, *args, **kwargs):
        if "stock" in kwargs and kwargs["stock"] in [1, True,"1"]:
            kwargs["stock"] = True
        else:
            kwargs["stock"] = False
        if "buffer" in kwargs and isinstance(kwargs['buffer'], basestring):
            kwargs['buffer'] =  get_buffer_or_none(kwargs['buffer'])
        if "ligand" in kwargs and isinstance(kwargs['ligand'], basestring):
            kwargs['ligand'] =  get_ligand_or_none(kwargs['ligand'])
        if "produced_by" in kwargs and isinstance(kwargs['produced_by'], basestring):
            kwargs['produced_by'] =  get_user_or_none(kwargs['produced_by'])
        object, created = super(LigandBatchManager, self).get_or_create(*args,**kwargs)
        return object, created


    def all_to_df(self):
        dic_ligand_batches = {}
        for batch in dic_ligand_batches:
            dic_ligand_batches[batch] = self.to_df()

    def to_df(self):
        df = read_frame(self.all())
        return df




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
        if "meta" in kwargs:
            print("*** Creating Study <{}>***".format(kwargs["meta"]["sid"]))
            if "user" in kwargs["meta"] and isinstance(kwargs["meta"]["user"], basestring):
                kwargs["meta"]["user"]=get_user_or_none(kwargs["meta"]["user"])
            if "status" in kwargs["meta"]:
                status = kwargs["meta"]["status"]
                if status:
                    # check if in selections
                    test = Status.get_choice(kwargs["meta"]["status"])

            this_study, created_s = super(StudyManager, self).get_or_create(*args, **kwargs["meta"])
            if bool(this_study.user):
                assign_perm("change_study",this_study.user, this_study)
                assign_perm("delete_study", this_study.user, this_study)

        if "raw_docs_fpaths" in kwargs:
            for fpath in kwargs["raw_docs_fpaths"]:
                raw_doc_dic = {"fpath": fpath}
                RawDoc = apps.get_model("flutype", model_name="RawDoc")
                raw_doc, created_rd = RawDoc.objects.get_or_create(**raw_doc_dic)
                this_study.files.add(raw_doc)

        if "measurements" in kwargs:
            for measurement in kwargs["measurements"]:
                measurement_dic = kwargs["measurements"][measurement]
                measurement_dic["study"] = this_study
                RawSpotCollection = apps.get_model("flutype", model_name="RawSpotCollection")
                _, _ = RawSpotCollection.objects.get_or_create(**measurement_dic)

        return this_study, created_s

class RawDocManager(models.Manager):
    def get_or_create(self, *args, **kwargs):
        if "fpath" in kwargs:
            raw_doc_dic = {}
            raw_doc_dic["sid"]= os.path.basename(kwargs["fpath"])
            with open(kwargs["fpath"], "rb") as f:
                raw_doc_dic["hash"] = md5(f)
                raw_doc, created = super(RawDocManager,self).get_or_create(**raw_doc_dic)
                raw_doc.file.save(os.path.basename(raw_doc_dic["sid"]), f)

        return raw_doc, created



class MeasurementManager(models.Manager):
    def get_or_create(self, *args, **kwargs):
        if "meta" in kwargs:
            print("*** Creating Measurement <{}>***".format(kwargs["meta"]["sid"]))

            this_measurement, created = super(MeasurementManager, self).get_or_create(*args, **kwargs["meta"])
            if bool(this_measurement.user):
                assign_perm("change_measurement",this_measurement.user, this_measurement)
                assign_perm("delete_measurement", this_measurement.user, this_measurement)
            this_measurement.studies.add(kwargs["study"])


        if "raw_docs_fpaths" in kwargs:
            for fpath in kwargs["raw_docs_fpaths"]:
                RawDoc = apps.get_model("flutype", model_name="RawDoc")
                raw_doc, created = RawDoc.objects.get_or_create(fpath = fpath)
                this_measurement.files.add(raw_doc)

        if "lig_mob_path" in kwargs:
            Galfile = apps.get_model("flutype", model_name="Galfile")
            lig_mob, created_m = Galfile.objects.get_or_create(lig_path=kwargs["lig_mob_path"])
            this_measurement.lig_mob = lig_mob
            this_measurement.save()
            lig_fix, created_l = Galfile.objects.get_or_create(lig_path=kwargs["lig_fix_path"])
            this_measurement.lig_fix =lig_fix
            this_measurement.save()
            kwargs["raw_spot_collection"]=this_measurement
            kwargs["raw_spots"] , _ = get_or_create_raw_spots(**kwargs)

            for raw_spot in kwargs["raw_spots"]:
                try:
                    this_measurement.ligands2.add(raw_spot.lig_mob_batch.ligand)
                    this_measurement.ligands1.add(raw_spot.lig_fix_batch.ligand)
                except:
                    pass

        if "steps_path" in kwargs:
            if kwargs["steps_path"]!= None:
                kwargs["raw_spot_collection"]= this_measurement
                Process = apps.get_model("flutype", model_name="Process")
                process , _ = Process.objects.get_or_create(**kwargs)
                this_measurement.process = process
                this_measurement.save()

        if "results" in kwargs:

            for result in kwargs["results"]:
                results_dic = kwargs["results"][result]
                results_dic["raw_spot"] = kwargs["raw_spots"]
                results_dic["meta"]["raw_spot_collection"]= this_measurement
                Spotcollection = apps.get_model("flutype", model_name="Spotcollection")
                spotcollection, created = Spotcollection.objects.get_or_create(**results_dic)

        return this_measurement, created

class ProcessManager(models.Manager):

    def get_or_create(self,*args,**kwargs):

        steps_path = kwargs["steps_path"]
        steps = read_tsv_table(steps_path)
        steps = clean_step_table(steps)
        steps = nan_to_none_in_pdtable(steps)
        sid = unique_ordering(steps)
        this_process, created = super(ProcessManager, self).get_or_create(sid=sid)
        steps["start"]=steps["start"].str.replace('.', '-')
        for _ , step in steps.iterrows():
            if step["start"]:
                unaware_datetime = datetime.datetime.strptime(step["start"], '%Y-%m-%d %H:%M')
                current_tz = timezone.get_current_timezone()
                step["start"] = current_tz.localize(unaware_datetime)

            Step= apps.get_model("flutype","Step")
            this_step = Step.objects.get(sid=step["step"])
            ProcessStep = apps.get_model("flutype","ProcessStep")
            this_process_step , _ = ProcessStep.objects.get_or_create(step=this_step,
                                                                      index=step["index"],
                                                                      start=step["start"],
                                                                      comment = step["comment"],
                                                                      raw_spot_collection=kwargs["raw_spot_collection"],
                                                                      process=this_process,
                                                                      user = get_user_or_none(step["user"])
                                                                      )
            if step["intensities"] is not None:
                intensity_fpath = os.path.join(os.path.dirname(steps_path),step["intensities"])
                intensities_path_dic = {"intensities" :intensity_fpath}
                GalFile = apps.get_model("flutype", "GalFile")
                this_gal_file, _ = GalFile.objects.get_or_create(**intensities_path_dic)
                this_process_step.intensities =this_gal_file
                this_process_step.save()

            if step["image"] is not None:
                image_fpath = os.path.join(os.path.dirname(steps_path),step["image"])
                with open(image_fpath, "rb") as f:
                    this_process_step.hash = md5(f)
                    this_process_step.save()
                    this_process_step.image.save(step["image"],File(f))

        return this_process, created




class GalFileManager(models.Manager):

    def get_or_create(self,*args, **kwargs):

        if "lig_path" in kwargs:
            kwargs["path"]= kwargs["lig_path"]
            this_gal, max_name = get_unique_galfile( "ligand_batch", **kwargs)
            if this_gal is None:
                sid = "ligand_batch_{:03}".format(max_name + 1)
                meta = {"sid":sid, "type":"ligand_batch"}
                this_gal, _ = super(GalFileManager, self).get_or_create(**meta)
                f = read_gal_file_to_temporaray_file(kwargs["path"])
                this_gal.file.save("{}.txt".format(this_gal.sid), File(f))
                f.close()
                return this_gal, True
            else:
                return this_gal, False

        if "std" in kwargs and kwargs["std"] is not None:
            kwargs["path"] = kwargs["std"]
            this_gal, max_name = get_unique_galfile("std", **kwargs)
            if this_gal is None:
                sid = "std_{:03}".format(max_name + 1)
                meta = {"sid": sid, "type":"std"}
                this_gal, _ = super(GalFileManager, self).get_or_create(**meta)
                f = read_gal_file_to_temporaray_file(kwargs["path"])
                this_gal.file.save("{}.txt".format(this_gal.sid), File(f))
                f.close()

                return this_gal, True
            else:
                return this_gal, False


        if "intensities" in kwargs and kwargs["intensities"] is not None:
            kwargs["path"]= kwargs["intensities"]

            this_gal, max_name = get_unique_galfile("intensity", **kwargs)
            if this_gal is None:
                sid = "intensity_{:03}".format(max_name + 1)
                meta = {"sid": sid, "type":"intensity"}
                this_gal, _ = super(GalFileManager, self).get_or_create(**meta)
                f = read_gal_file_to_temporaray_file(kwargs["path"])
                this_gal.file.save("{}.txt".format(this_gal.sid), File(f))
                f.close()

                return this_gal, True
            else:
                return this_gal, False





class SpotcollectionManager(models.Manager):
    def get_or_create(self, *args, **kwargs):

        if "meta" in kwargs:
            meta = kwargs["meta"]
            print("*** Creating Result <{}>***".format(kwargs["meta"]["sid"]))
            this_spot_collection, created = super(SpotcollectionManager, self).get_or_create(*args, **meta)
            if bool(this_spot_collection.raw_spot_collection.user):
                assign_perm("change_spot_collection", this_spot_collection.raw_spot_collection.user, this_spot_collection)
                assign_perm("delete_spot_collection", this_spot_collection.raw_spot_collection.user, this_spot_collection)

        if "raw_docs_fpaths" in kwargs:
            for fpath in kwargs["raw_docs_fpaths"]:
                raw_doc_dic = {"fpath": fpath}
                RawDoc = apps.get_model("flutype", model_name="RawDoc")
                raw_doc, created = RawDoc.objects.get_or_create(**raw_doc_dic)
                this_spot_collection.files.add(raw_doc)



        if "intensities" in kwargs:
            kwargs["spot_collection"]=this_spot_collection
            create_spots(**kwargs)

            GalFile = apps.get_model("flutype", "GalFile")

            intensity_dic = {"intensities": kwargs["intensities"]}
            object_gal_file, _ = GalFile.objects.get_or_create(**intensity_dic)
            this_spot_collection.int_gal = object_gal_file
            this_spot_collection.save()

            if "std" in kwargs:
                std_dic = {"std": kwargs["std"]}
                object_gal_file, _ = GalFile.objects.get_or_create(**std_dic)
                this_spot_collection.std_gal = object_gal_file
                this_spot_collection.save()



        return this_spot_collection, created


class RawSpotManager(models.Manager):
    def get_or_create(self, *args, **kwargs):

        if "lig_fix_batch" in kwargs and isinstance(kwargs['lig_fix_batch'], basestring):
            LigandBatch = apps.get_model("flutype","LigandBatch")
            ligand_object = LigandBatch.objects.get_subclass(sid=kwargs['lig_fix_batch'])
            kwargs["lig_fix_batch"] = ligand_object


        if "lig_mob_batch" in kwargs and isinstance(kwargs['lig_mob_batch'], basestring):
            LigandBatch = apps.get_model("flutype","LigandBatch")
            ligand_object = LigandBatch.objects.get_subclass(sid=kwargs["lig_mob_batch"])
            kwargs["lig_mob_batch"] = ligand_object

        object, created = super(RawSpotManager, self).get_or_create(**kwargs)
        return object, created




















