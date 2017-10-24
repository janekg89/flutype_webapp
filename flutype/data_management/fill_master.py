

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

from flutype.data_management.master import LIGAND_BATCHES, LIGANDS, STEPS, MASTERPATH, Master, BASEPATH
from flutype.helper import read_complex, read_ligands, read_ligand_batches ,read_steps


###############################################

# fix for py3
try:
    input = raw_input
except NameError:
    pass


def write_all_ligands(master_path):
    ma = Master(master_path)
    ma.write_ligands({"complex":read_complex()})
    for ligand in LIGANDS:
        ma.write_ligands({ligand:read_ligands(ligand)})

def write_all_ligand_batches(master_path):
    ma = Master(master_path)
    for ligand_batches in LIGAND_BATCHES:
        ma.write_ligand_batches({ligand_batches:read_ligand_batches(ligand_batches)})

def write_all_steps(master_path):
    ma = Master(master_path)
    for step in STEPS:
        print(step)
        ma.write_steps({step: read_steps(step)})


####################################################################
if __name__ == "__main__":
    ''' 
    WRITES EVERYTHING IN MASTER;
    !!! OVERWRITES EXISTING DATA !!!
    '''
    write_master = True
    # path to the master folder
    path_master = os.path.join(BASEPATH, "master_neu")

    if write_master:
        write_all_ligands(path_master)
        write_all_ligand_batches(path_master)
        write_all_steps(path_master)


