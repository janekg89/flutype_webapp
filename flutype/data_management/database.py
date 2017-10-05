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


def fill_study():
    pass

if __name__ == "__main__":

    pass





