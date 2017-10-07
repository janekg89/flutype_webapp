"""
Script for filling database from backup
"""
from __future__ import print_function, absolute_import, division
import os
import sys
from django.core.files import File
import warnings
import re
import pandas as pd
from PIL import Image
from django.core.files import File
from django_pandas.io import read_frame
from datetime import timedelta
###########################################################
# setup django (add current path to sys.path)
path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))

if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flutype_webapp.settings")

import django
django.setup()

###########################################################
from django.contrib.auth.models import User
import flutype.data_management.fill_master
from flutype.helper import md5
from flutype.data_management.fill_database import DBDjango
from flutype.helper import get_or_create_object_from_dic
from flutype.data_management.master import LIGAND_BATCHES, LIGANDS, STEPS
from flutype.models import (Peptide,
                            PeptideBatch,
                            Virus,
                            Complex,
                            ComplexBatch,
                            VirusBatch,
                            Antibody,
                            AntibodyBatch,
                            Ligand,
                            LigandBatch,
                            RawSpotCollection,
                            SpotCollection,
                            RawSpot,
                            Spot,
                            Spotting,
                            Quenching,
                            Incubating,
                            Washing,
                            Drying,
                            Scanning,
                            Blocking,
                            ProcessStep,
                            Process,
                            GalFile,
                            Step,
                            Study
                            )


class DatabaseDJ(object):

    def __init__(self):
        self.ligands = LIGANDS
        self.steps = STEPS
        self.ligand_batches = LIGAND_BATCHES




    def get_or_create_ligand(self,ligand,ligand_dic):
        return get_or_create_object_from_dic(ligand,ligand_dic)






if __name__ == "__main__":
    pass





