import os

from flutype.data_management.master import Master,\
    Study, Measurement,MeasurementResult, BASEPATH, LIGAND_BATCHES, LIGANDS, STEPS
from flutype.data_management.database import DatabaseDJ
from flutype.helper import fill_multiple_models_from_dict
from django.test import TestCase


MASTERPATH = os.path.join(BASEPATH, "master_new")


class DatabaseDJTestCase(TestCase):
    def setUp(self):
        self.db = DatabaseDJ()
        self.ma = Master(MASTERPATH)


    def test_get_or_create_ligand(self):
        ligands = self.ma.read_ligands()
        ligand_batches = self.ma.read_ligand_batches()
        fill_multiple_models_from_dict(ligand_batches)

