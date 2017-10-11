import os

from flutype.data_management.master import Master,\
    Study, Measurement,MeasurementResult, BASEPATH, LIGAND_BATCHES, LIGANDS, STEPS
from flutype.data_management.database import DatabaseDJ
from flutype.helper import fill_multiple_models_from_dict, create_study
from django.test import TestCase
from flutype.data_management.fill_users import create_users, user_defs



MASTERPATH = os.path.join(BASEPATH, "master_new")


class DatabaseDJTestCase(TestCase):
    def setUp(self):
        create_users(user_defs=user_defs)
        self.db = DatabaseDJ()
        self.ma = Master(MASTERPATH)

    def test_update_ligands(self):
        ligands = self.ma.read_ligands()
        self.db.update_ligands_or_batches(ligands)


    def test_update_complex(self):
        ligands = self.ma.read_ligands()
        complex = self.ma.read_complex()
        self.db.update_ligands_or_batches(ligands)
        self.db.update_ligands_or_batches(complex)

    def test_update_batches(self):
        ligands = self.ma.read_ligands()
        complex = self.ma.read_complex()
        self.db.update_ligands_or_batches(ligands)
        self.db.update_ligands_or_batches(complex)
        ligand_batches = self.ma.read_ligand_batches()
        self.db.update_ligands_or_batches(ligand_batches)

    def test_update_steps(self):
        ligands = self.ma.read_ligands()
        complex = self.ma.read_complex()

        self.db.update_ligands_or_batches(ligands)
        self.db.update_ligands_or_batches(complex)

        ligand_batches = self.ma.read_ligand_batches()
        self.db.update_ligands_or_batches(ligand_batches)

        steps = self.ma.read_steps()

        self.db.update_steps(steps)

    def test_update_study(self):
        steps = self.ma.read_steps()
        self.db.update_steps(steps)

        studies= self.ma.read_studies()
        self.db.update_studies(studies)

    def test_getattrubute(self):
        print(LIGANDS)
        ligands = self.ma.read_ligands()



