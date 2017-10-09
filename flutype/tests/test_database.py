import os

from flutype.data_management.master import Master,\
    Study, Measurement,MeasurementResult, BASEPATH, LIGAND_BATCHES, LIGANDS, STEPS
from flutype.data_management.database import DatabaseDJ
from flutype.helper import fill_multiple_models_from_dict, create_study
from django.test import TestCase
from flutype.data_management.fill_users import create_users, user_defs

from flutype.models import Peptide
import sys

MASTERPATH = os.path.join(BASEPATH, "master_new")


class DatabaseDJTestCase(TestCase):
    def setUp(self):
        self.db = DatabaseDJ()
        self.ma = Master(MASTERPATH)
        create_users(user_defs=user_defs)


    def test_get_or_create_ligand(self):
        studies= self.ma.read_studies()
        for study in studies:
            create_study(**studies[study])


    def test_getattrubute(self):
        print(LIGANDS)
        ligands = self.ma.read_ligands()

