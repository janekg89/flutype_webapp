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
import re


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


def unique_ordering(steps):
    if steps["step"].empty:
        vals = "NoSteps"
    else:
        order_steps = steps["step"]
        vals = '-'.join(order_steps)
    return vals

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
            if value == "":
                value = None
    return d


def read_tsv_table(fpath):
    table = pd.read_csv(fpath, sep="\t", encoding='utf-8', dtype=str)
    table.replace([np.NaN], [None], inplace=True)
    return table

def get_or_create_raw_spots(**kwargs):
    raw_spots = []
    RawSpot = apps.get_model("flutype","RawSpot")
    lig_mob = read_gal_file(kwargs["lig_mob_path"])
    lig_fix = read_gal_file(kwargs["lig_fix_path"])
    spots = pd.DataFrame(lig_fix[["Name","Row","Column"]], columns=["Name","Row","Column"])
    spots = spots.rename(columns={"Name":"lig_fix_batch"})
    spots["lig_mob_batch"]= lig_mob["Name"].values
    spots["raw_spot_collection"]=kwargs["raw_spot_collection"]
    print(spots)
    for k, spot in spots.iterrows():
        RawSpot.objects.create(**spot)
    return raw_spots



def create_spots(**kwargs):
    Spot = apps.get_model("flutype","Spot")
    spots = read_gal_file(kwargs["intensities"])
    if "std" in kwargs:
        spots["std"]=kwargs["std"].values



def get_unique_galfile(name_presilbe, **kwargs):
    GalFile = apps.get_model("flutype", model_name="GalFile")
    this_gal = read_gal_file(kwargs["path"])
    max_name = 0
    for gal_file in GalFile.objects.all():
        result = re.search(name_presilbe + '(.*)', gal_file.sid)
        if bool(result):
            if int(result.group(1)) > max_name:
                max_name = int(result.group(1))

            df_gal = pd.read_csv(gal_file.file.path, sep='\t', index_col="ID")
            if df_gal.equals(this_gal):
                return gal_file, max_name

    return None, max_name

def read_gal_file(fpath):
    try:
        this_gal = pd.read_csv(fpath, sep='\t', index_col="ID")
        this_gal.replace([np.NaN], [None], inplace=True)
        this_gal.replace(["NO"], [None], inplace=True)


    except:
        this_gal = pd.read_csv(fpath, sep='\t')
        this_gal = raws_and_cols_to_gal_file(this_gal)
        this_gal.replace([np.NaN], [None], inplace=True)


    return this_gal

def gal_file_to_rows_and_cols(this_gal):
    pass


def raws_and_cols_to_gal_file(this_gal):
    this_gal = this_gal.stack()
    data = {"ID":range(1, 1 + len(this_gal.values)),
            "Row": this_gal.index.get_level_values(0),
            "Column": this_gal.index.get_level_values(1),
            "Name": this_gal.values
            }
    df = pd.DataFrame(data=data)
    df1 = df.set_index("ID")
    return df1



def create_study(**study_dic):

    Study = apps.get_model("flutype", model_name="Study")
    study, created = Study.objects.get_or_create(**study_dic["meta"])
    ##########################################################


def add_raw_docs_model(model,raw_docs_fpaths):
    for fpath in raw_docs_fpaths:
        raw_doc ,_ = get_or_create_raw_doc(fpath)
        model.files.add(raw_doc)


def get_or_create_raw_doc(fpath):
    RawDoc = apps.get_model("flutype", model_name="RawDoc")
    raw_doc, created = RawDoc.objects.get_or_create()
    with open(fpath, "rb") as f:
        raw_doc.file.save(os.path.basename(fpath), File(f))
    return raw_doc, created


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
    object, created = model.objects.get_or_create(**kwargs)

    return object, created


def create_objects_from_df(object_n , object_df):
    for _, dict_single in object_df.iterrows():
        get_or_create_object_from_dic(object_n , **dict_single)



def fill_multiple_models_from_dict(object_dics):
    for object, object_df in object_dics.items():
       create_objects_from_df(object, object_df)





