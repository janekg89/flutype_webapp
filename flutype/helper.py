from __future__ import absolute_import, print_function, unicode_literals
from django.core.files.storage import FileSystemStorage
from flutype_webapp.settings import MEDIA_ROOT
import os
import hashlib
import csv
import pandas as pd


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
    with open(fpath, 'r') as f:
        reader = csv.reader(f, delimiter="\t")
    return dict(reader)
def read_tsv_table(fpath):
    return pd.read_csv(fpath, sep="\t", encoding='utf-8', dtype=str)