"""
Script for filling database from backup
"""
from __future__ import print_function, absolute_import, division
import os
import sys

###########################################################
# setup django (add current path to sys.path)
path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))
from django.apps import apps

if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flutype_webapp.settings")

import django
django.setup()

###########################################################
from flutype.helper import md5, fill_multiple_models_from_dict
from flutype.data_management.master import LIGAND_BATCHES, LIGANDS, STEPS



class DatabaseDJ(object):

    def __init__(self):
        self.ligands = LIGANDS
        self.steps = STEPS
        self.ligand_batches = LIGAND_BATCHES

    def update_ligands_or_batches(self,ligands):
        fill_multiple_models_from_dict(ligands)

    def update_steps(self,steps):
        fill_multiple_models_from_dict(steps)

    def update_studies(self,study_dics):
        Study = apps.get_model("flutype", model_name="Study")
        for study_sid in study_dics:
            Study.objects.get_or_create(**study_dics[study_sid])


if __name__ == "__main__":
    pass





