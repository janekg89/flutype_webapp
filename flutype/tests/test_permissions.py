from django.test import TestCase, Client, TransactionTestCase
from flutype.data_management.fill_users import create_users, user_defs
from flutype_webapp.settings import DEFAULT_USER_PASSWORD
from flutype.data_management.master import Master, BASEPATH, Study
from flutype.data_management.fill_database import DatabaseDJ
from django.shortcuts import redirect

import os

class ChangeStudyTestCase(TransactionTestCase):

    @classmethod
    def setUp(self):
        create_users(user_defs=user_defs)
        MASTERPATH = os.path.join(BASEPATH, "master")
        study_path = os.path.join(BASEPATH, "master/studies/170509-microwell")
        self.ma = Master(MASTERPATH)
        study = Study(study_path).read()
        study_dic = {"170509-microwell": study}
        self.db = DatabaseDJ(self.ma)
        ligands = self.ma.read_ligands()
        complex = self.ma.read_complex()
        buffer = self.ma.read_buffer()
        self.db.update_ligands_or_batches(ligands)
        self.db.update_ligands_or_batches(complex)
        self.db.update_ligands_or_batches(buffer)
        ligand_batches = self.ma.read_ligand_batches()
        self.db.update_ligands_or_batches(ligand_batches)
        steps = self.ma.read_steps()
        self.db.update_steps(steps)
        self.db.update_studies(study_dic)
        # only create once
        self.c = Client()
        self.c.login(username='hmemczak', password=DEFAULT_USER_PASSWORD)


    def tearDown(self):
        create_users(user_defs=None, delete_all=True)

    def test_permission_allowed(self):
        url  = redirect('study',sid="170509-microwell")
        response = self.c.get(url, {})
        print(response)



