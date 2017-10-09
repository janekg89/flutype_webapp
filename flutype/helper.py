from __future__ import absolute_import, print_function, unicode_literals
from django.core.files.storage import FileSystemStorage
from flutype_webapp.settings import MEDIA_ROOT
from django.contrib.auth.models import User
import os
import hashlib
import pandas as pd
from django.apps import apps
import numpy as np
import datetime
from django.core.files import File



CHAR_MAX_LENGTH = 50


def generate_tree(path):
    path_templates = os.path.join(path, "../../../", "templates/flutype/")
    path_file = os.path.join(path_templates, "tree.html")
    #################
    os.system("tree {} -oH {} . --nolinks".format(path,path_file))
    return os.path.isfile(path_file)

def tar_tree(path):
    directory_dir = os.path.join(path,"170929-tutorial/")
    directory_to = os.path.join(path,"170929-tutorial/raw_docs/")
    path_file = os.path.join(directory_to,"tree.tar.gz")

    os.system("tar -czf {} {}".format(path_file,directory_dir))
    return os.path.isfile(path_file)


def md5(f):
    hash_md5 = hashlib.md5()
    for chunk in iter(lambda: f.read(4096), b""):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()



class OverwriteStorage(FileSystemStorage):
    """
    Overwrite storage overwrites existing names by deleting the resources.
    ! Use with care. This deletes files from the media folder !
    """

    def get_available_name(self, name, **kwargs):
        if self.exists(name):
            os.remove(os.path.join(MEDIA_ROOT, name))
        return name

def read_tsv_diconary(fpath):
    d={}
    with open(fpath, 'r') as f:
        for line in f:
            line =line.split("\t")
            if len(line) == 1:
                line.append("")
            key = line[0].strip()
            value = line[1].strip()
            if value == "TRUE":
                value = True
            d[key] = value
    return d


def read_tsv_table(fpath):
    table = pd.read_csv(fpath, sep="\t", encoding='utf-8', dtype=str)
    table.replace([np.NaN], [None], inplace=True)
    return table



def create_study(**study_dic):

    Study = apps.get_model("flutype", model_name="Study")
    study, created = Study.objects.get_or_create(**study_dic["meta"])
    ##########################################################
    #Raw Docs
    add_raw_docs_model(study, study_dic["raw_docs_fpaths"])
    ##########################################################
    #measurements
    for measurement in study_dic["measurements"]:
        get_or_create_measurement( study, **study_dic["measurements"][measurement])

def add_raw_docs_model(model,raw_docs_fpaths):
    for fpath in raw_docs_fpaths:
        raw_doc ,_ = get_or_create_raw_doc(fpath)
        model.files.add(raw_doc)

def get_or_create_gal_file(fpath):
    pass


def get_or_create_raw_doc(fpath):
    RawDoc = apps.get_model("flutype", model_name="RawDoc")
    raw_doc, created = RawDoc.objects.get_or_create()
    raw_doc.file.save(os.path.basename(fpath), File(open(fpath, "rb")))
    return raw_doc, created


def get_or_create_measurement(study,**measurement_dic):

    Measurement = apps.get_model("flutype", model_name="Measurement")
    ##########################################################
    # steps

    measurement, created = Measurement.objects.get_or_create(study=study,**measurement_dic["meta"])
    ##########################################################


    # Raw Docs
    add_raw_docs_model(measurement, measurement_dic["raw_docs_fpaths"])
    ##########################################################
    # gal_file



    ##########################################################
    # results

def get_or_create_process():
    pass







def get_model_by_name(name):
    Model = apps.get_model("flutype",model_name=name)
    return Model

def get_user_or_none(user):

    if user is None:
            user = None
    else:
        user = User.objects.get(username=user)

    return user

def get_ligand_or_none(ligand):
    Ligand = apps.get_model("flutype", model_name="Ligand")
    if ligand is None:
            ligand = None
    else:
        ligand = Ligand.objects.get(sid=ligand)

    return ligand

def get_duration_or_none(duration):
    if duration is None:
        duration = None
    else:
        dursplit = duration.split(":")
        duration = datetime.timedelta(days=int(dursplit[0]),
                                      hours=int(dursplit[1]),
                                      minutes=int(dursplit[2]),
                                      seconds=int(dursplit[3]))

    return duration



def get_or_create_object_from_dic(object_n, **kwargs):

    object_capitalized = object_n.capitalize()
    model = get_model_by_name(object_capitalized)
    if "user" in kwargs:
        kwargs["user"]=get_user_or_none(kwargs["user"])
    if "produced_by" in kwargs:
        kwargs["produced_by"]=get_user_or_none(kwargs["produced_by"])
    if "duration" in kwargs:
        kwargs["duration"] = get_duration_or_none(kwargs["duration"])



    ###################################################
    if 'complex_ligands' in kwargs:
            ligands_str = kwargs['complex_ligands']
            del kwargs['complex_ligands']
            object, created = model.objects.get_or_create(**kwargs)
            for ligand_sid in ligands_str.split('-'):
                ligand = get_ligand_or_none(ligand_sid)
                object.complex_ligands.add(ligand)
    ####################################################
    elif 'ligand' in kwargs:
        ligand= get_ligand_or_none(kwargs['ligand'])
        del kwargs['ligand']
        object, created = model.objects.get_or_create(ligand=ligand,
                                                      **kwargs)

    else:
        object, created = model.objects.get_or_create(**kwargs)
    #for key in dict:
    #    if key!= "sid":
    #       object.__setattr__(key,dict[key])
    return object, created


def create_objects_from_df(object_n , object_df):
    for _, dict_single in object_df.iterrows():
        get_or_create_object_from_dic(object_n , **dict_single)



def fill_multiple_models_from_dict(object_dics):
    for object, object_df in object_dics.items():
       create_objects_from_df(object, object_df)





