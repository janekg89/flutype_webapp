from __future__ import print_function, absolute_import, division
import os
import sys

import cv2
import csv
import re
import pandas as pd
import numpy as np
from django.core.files import File

###############################################
# setup django (add current path to sys.path)
path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))

if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flutype_webapp.settings")

import django
django.setup()

import flutype.data_management.fill_database
from flutype.models import RawSpotCollection
from flutype.helper import read_tsv_diconary , read_tsv_table

###############################################

# fix for py3
try:
    input = raw_input
except NameError:
    pass

class BaseAll(object):
    def __init__(self, path):
        self.path = path


class Master(BaseAll):
    """ Class for operations on master files. """
    def __init__(self, path):

        BaseAll.__init__(self,path)
        self.path_study = os.path.join(self.path, "studies")
        self.studies = set(next(os.walk(self.path_study))[1])
        self.path_data_tables = os.path.join(self.path, "data_tables")
        self.path_mob_lig = os.path.join(self.path, "mob_lig")
        self.path_fix_lig = os.path.join(self.path, "fix_lig")


class Base(BaseAll):
    def __init__(self,path):
        BaseAll.__init__(self,path)
        self.path_meta = os.path.join(self.path, "meta.tsv")
        self.meta = read_tsv_diconary(self.path_meta)
        self.sid = self.meta["sid"]


class Study(Base):
    "Class for operations on a study"
    def __init__(self, path):
        Base.__init__(self,path)
        self.measurements_fnames = set(next(os.walk(path))[1]) - {'raw_docs'}
        self.path_raw_docs = os.path.join(self.path, "raw_docs")
        self.raw_docs_fnames = set(next(os.walk(self.path_raw_docs))[1])
        self.task = self.meta["task"]
        self.result = self.meta["result"]

    def read(self):
        pass

    def write(self,dict):
        pass



class Measurement(Base):
    "Class for operations on a Measurement"
    def __init__(self, path):
        Base.__init__(self,path)
        self.Study = Study(os.path.join(self.path, ".."))
        self.path_mob_lig = os.path.join(self.path, "mob_lig")
        self.path_fix_lig = os.path.join(self.path, "fix_lig")
        self.path_steps = os.path.join(self.path, "steps.tsv")
        self.steps = read_tsv_table(self.path_steps)

    def read(self):
        pass

    def write(self, dict):
        pass


class MeasurementResult(Base):
    "Class for operations on "
    def __init__(self, path):
        Base.__init__(self,path)
        self.Measurement = Measurement(os.path.join(self.path, ".."))
        self.path_intensity = os.path.join(self.path, "intensity.tsv")
        self.path_std = os.path.join(self.path, "std.tsv")
        self.intensity = read_tsv_table(self.path_intensity)
        self.std = read_tsv_table(self.path_std)
        self.comment = self.meta["comment"]

    def read(self):
        pass

    def write(self, dict):
            pass


#todo how to you call it that you can write -- and - commands in the terminal with arguments