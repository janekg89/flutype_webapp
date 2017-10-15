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
import re
import tempfile
import io
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

CHAR_MAX_LENGTH = 50

def empty_list(max):
    list = []
    for n in range(max):
        list.append('')
    return list

def generate_tree(path):
    path_templates = os.path.join(BASE_DIR, "flutype/templates/flutype/")
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
            if value == "":
                value = None
            if value =="FALSE":
                value = False
            d[key] = value

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
    spots = spots.rename(columns={"Name":"lig_fix_batch", "Row":"row","Column":"column"})
    spots["lig_mob_batch"]= lig_mob["Name"].values
    spots["raw_spot_collection"]=kwargs["raw_spot_collection"]
    for k, spot in spots.iterrows():
        #print(spot["lig_fix_batch"])
        raw_spot, created = RawSpot.objects.get_or_create(**spot)
        raw_spots.append(raw_spot)
    return raw_spots, created



def create_spots(**kwargs):
    Spot = apps.get_model("flutype","Spot")
    intensities = read_gal_file(kwargs["intensities"])
    spots =pd.DataFrame(intensities["Name"].values, columns=["intensity"])
    spots["raw_spot"] = kwargs["raw_spot"]
    spots["spot_collection"] = kwargs["spot_collection"]
    if "std" in kwargs:
        std = read_gal_file(kwargs["std"])
        list_std = std["Name"].values
        spots["std"]=[float(i) for i in list_std]

    for k, spot in spots.iterrows():
        this_spot,_ = Spot.objects.get_or_create(raw_spot = spot["raw_spot"],
                                                spot_collection = spot["spot_collection"])


        if "std" in kwargs:
            this_spot.intensity = spot["intensity"]
            this_spot.std = spot["std"]
            this_spot.save()

        else:
            this_spot.intensity = spot["intensity"]
            this_spot.save()







def get_unique_galfile(type, **kwargs):

    GalFile = apps.get_model("flutype", model_name="GalFile")
    this_gal = read_gal_file(kwargs["path"])
    max_name = 0
    for gal_file in GalFile.objects.filter(type=type):
        #updates name number
        result = re.search(type + '_(.*)', gal_file.sid)
        if int(result.group(1)) > max_name:
            max_name = int(result.group(1))
        #checks if equal
        df_gal = read_gal_file(gal_file.file.path)
        if df_gal.equals(this_gal):

            return gal_file, max_name

    return None, max_name

def read_gal_file(fpath):
    try:
        this_gal = pd.read_csv(fpath, sep='\t', index_col="ID", dtype=str)
        this_gal.replace([np.NaN], [None], inplace=True)
        this_gal.replace(["NO"], [None], inplace=True)
        this_gal.replace(["No"], [None], inplace=True)



    except:
        this_gal = pd.read_csv(fpath, sep='\t', index_col = 0,  dtype=str)
        this_gal = raws_and_cols_to_gal_file(this_gal)
        this_gal.replace([np.NaN], [None], inplace=True)

    return this_gal

def read_gal_file_to_temporaray_file(fpath):
    #f = tempfile.TemporaryFile()
    f= io.StringIO()

    gal_file = read_gal_file(fpath)
    gal_file.to_csv(f, sep=str('\t'), index="True", encoding='utf-8')
    return f


def gal_file_to_rows_and_cols(this_gal):
    pass


def raws_and_cols_to_gal_file(this_gal):
    this_gal = this_gal.stack()
    id = range(1, 1 + len(this_gal.values))
    data = {"ID":id ,
            "Row": list(map(str,this_gal.index.get_level_values(0))),
            "Column": list(map(str,this_gal.index.get_level_values(1))),
            "Name":list(map(str, this_gal.values))
            }
    df = pd.DataFrame(data=data)
    df1 = df.set_index("ID")
    return df1



def create_study(**study_dic):

    Study = apps.get_model("flutype", model_name="Study")
    study, created = Study.objects.get_or_create(**study_dic["meta"])
    ##########################################################

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





