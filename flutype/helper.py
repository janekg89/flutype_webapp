from __future__ import absolute_import, print_function, unicode_literals
from django.core.files.storage import FileSystemStorage
from flutype_webapp.settings import MEDIA_ROOT
from polymorphic.utils import reset_polymorphic_ctype
import os
import hashlib
import pandas as pd
from django.apps import apps


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
            d[key] = value

    return d


def read_tsv_table(fpath):
    return pd.read_csv(fpath, sep="\t", encoding='utf-8', dtype=str)


def get_model_by_name(name):
    Model = apps.get_model("flutype",model_name=name)
    #reset_polymorphic_ctype(Model,ignore_existing=True)
    return Model


def get_or_create_object_from_dic(object, **kwargs):
    object_capitalized = object.capitalize()
    model = get_model_by_name(object_capitalized)
    print(model.objects)

    object, created = model.objects.get_or_create(kwargs)
    #for key in dict:
    #    if key!= "sid":
    #       object.__setattr__(key,dict[key])
    return object, created


def create_objects_from_df(object , object_df):
    for _, dict_single in object_df.iterrows():
        get_or_create_object_from_dic(object , **dict_single)



def fill_multiple_models_from_dict(object_dics):
    for object, object_df in object_dics.items():
       create_objects_from_df(object, object_df)




