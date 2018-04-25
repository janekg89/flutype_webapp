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
from flutype.helper import  fill_multiple_models_from_dict
from flutype.data_management.master import LIGAND_BATCHES, LIGANDS, STEPS, MASTERPATH,Master, BASEPATH

class DatabaseDJ(object):

    def __init__(self,Master):
        self.ma = Master
        self.ligands = self.ma.ligands
        self.steps = self.ma.steps
        self.ligand_batches = self.ma.ligand_batches


    def update_ligands_or_batches(self,ligands):
        fill_multiple_models_from_dict(ligands)

    def update_steps(self, steps):
        fill_multiple_models_from_dict(steps)

    def update_studies(self, study_dics):
        Study = apps.get_model("flutype", model_name="Study")
        for study_sid in study_dics:
            Study.objects.get_or_create(**study_dics[study_sid])

    def update_db(self):
        ligands = self.ma.read_ligands()
        complex = self.ma.read_complex()
        buffer = self.ma.read_buffer()



        self.update_ligands_or_batches(ligands)
        self.update_ligands_or_batches(complex)
        self.update_ligands_or_batches(buffer)


        ligand_batches = self.ma.read_ligand_batches()
        self.update_ligands_or_batches(ligand_batches)

        steps = self.ma.read_steps()
        self.update_steps(steps)

        studies = self.ma.read_studies()
        self.update_studies(studies)





if __name__ == "__main__":
    MASTERPATH = os.path.join(BASEPATH, "master_2018_03_02")

    ma = Master(MASTERPATH)
    DatabaseDJ(ma).update_db()





