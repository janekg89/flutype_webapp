#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flutype_webapp.settings import DEFAULT_USER_PASSWORD
from django.test import TestCase, Client, TransactionTestCase, tag



from flutype.data_management.fill_users import create_users, user_defs
from flutype.data_management.fill_database import DatabaseDJ

from flutype.models import RawSpotCollection, SpotCollection, Process
from flutype.tests.test_fill_database import MASTERPATH
from flutype.data_management.master import Master, BASEPATH, Study
from django.db import transaction
import os

class ViewTestCaseNoDataLogOut(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_users(user_defs=user_defs)


    def setUp(self):
        # only create once
        self.c = Client()

    def tearDown(self):
        create_users(user_defs=None, delete_all=True)

    def test_login_view(self):
        response = self.c.post('/login/', {})
        status = response.status_code
        self.assertEqual(status, 200, "login view 200")
        self.assertContains(response, "<h1>Login</h1>")

    def test_logout_view(self):
        response = self.c.get('/logout/', {})
        status = response.status_code
        self.assertEqual(status, 200, "logout view 200")
        self.assertContains(response, "<h1>Logged out</h1>")

    def test_about_view(self):
        response = self.c.post('/flutype/about/', {})
        status = response.status_code
        self.assertEqual(status, 200, "about view 200")
        self.assertContains(response, "<h2>FluType</h2>")

    #######################################################################
    # No permission
    def test_index_view_302(self):
        response = self.c.post('/flutype/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

    def test_redirect_if_not_logged_in(self):
        response = self.c.get('/flutype/', {})
        self.assertRedirects(response, '/login/?next=/flutype/')

    def test_antibody_view_302(self):
        response = self.c.post('/flutype/antibodies_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

        response = self.c.post('/flutype/antibodies_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

        response = self.c.post('/flutype/antibodies/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

    def test_antibodybatches_view_302(self):
        response = self.c.post('/flutype/antibodybatches/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

        response = self.c.post('/flutype/antibodybatches_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

        response = self.c.post('/flutype/antibodybatches_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

    def test_viruses_view_302(self):
        response = self.c.post('/flutype/viruses/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

        response = self.c.post('/flutype/viruses_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

        response = self.c.post('/flutype/viruses_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

    def test_virusbatches_view_302(self):
        response = self.c.post('/flutype/virusbatches/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

        response = self.c.post('/flutype/virusbatches_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

        response = self.c.post('/flutype/virusbatches_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

    def test_peptides_view_302(self):
        response = self.c.post('/flutype/peptides/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

        response = self.c.post('/flutype/peptides_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

        response = self.c.post('/flutype/peptides_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

    def test_peptidebatches_view_302(self):
        response = self.c.post('/flutype/peptidebatches/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

        response = self.c.post('/flutype/peptidebatches_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

        response = self.c.post('/flutype/peptidebatches_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

    def test_processes_view_302(self):
        response = self.c.post('/flutype/processes/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

    def test_users_view_302(self):
        response = self.c.post('/flutype/users/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

    def test_myexperiments_view_302(self):
        response = self.c.post('/flutype/mymeasurements/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

    def test_password_view_302(self):
        response = self.c.post('/flutype/password/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")


class ViewTestCaseNoDataLogedIn(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_users(user_defs=user_defs)

    def setUp(self):
        # only create once
        self.c = Client()
        self.c.login(username='mkoenig', password=DEFAULT_USER_PASSWORD)

    def tearDowns(self):
        create_users(user_defs=None, delete_all=True)

    def test_index_view_200(self):
        response = self.c.post('/flutype/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "Studies")

    def test_antibody_view_200(self):
        response = self.c.post('/flutype/antibodies_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

        response = self.c.post('/flutype/antibodies_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

        response = self.c.post('/flutype/antibodies/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

    def test_antibodybatches_view_200(self):
        response = self.c.post('/flutype/antibodybatches/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

        response = self.c.post('/flutype/antibodybatches_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

        response = self.c.post('/flutype/antibodybatches_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

    def test_viruses_view_200(self):
        response = self.c.post('/flutype/viruses/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

        response = self.c.post('/flutype/viruses_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

        response = self.c.post('/flutype/viruses_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

    def test_virusbatches_view_200(self):
        response = self.c.post('/flutype/virusbatches/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

        response = self.c.post('/flutype/virusbatches_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

        response = self.c.post('/flutype/virusbatches_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

    def test_peptides_view_200(self):
        response = self.c.post('/flutype/peptides/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

        response = self.c.post('/flutype/peptides_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

        response = self.c.post('/flutype/peptides_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

    def test_peptidebatches_view_200(self):
        response = self.c.post('/flutype/peptidebatches/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

        response = self.c.post('/flutype/peptidebatches_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

        response = self.c.post('/flutype/peptidebatches_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

    def test_processes_view_200(self):
        response = self.c.post('/flutype/processes/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

    def test_users_view_200(self):
        response = self.c.post('/flutype/users/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "mkoenig")

    def test_myexperiments_view_200(self):
        response = self.c.post('/flutype/mymeasurements/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

class ViewTestCaseOneCollectionLogedIn(TransactionTestCase):
    def setUp(self):
        create_users(user_defs=user_defs)

        MASTERPATH = os.path.join(BASEPATH, "master")
        study_path = os.path.join(BASEPATH, "master/studies/170509-microwell")
        self.ma = Master(MASTERPATH)
        study = Study(study_path).read()
        study_dic = {"170509-microwell": study}
        self.db = DatabaseDJ(self.ma)
        ligands = self.ma.read_ligands()
        complex =  self.ma.read_complex()
        self.db.update_ligands_or_batches(ligands)
        self.db.update_ligands_or_batches(complex)

        ligand_batches =  self.ma.read_ligand_batches()
        self.db.update_ligands_or_batches(ligand_batches)

        steps =  self.ma.read_steps()
        self.db.update_steps(steps)
        self.db.update_studies(study_dic)

        self.c = Client()
        self.c.login(username='hmemczak', password=DEFAULT_USER_PASSWORD)

    def tearDown(self):
        create_users(user_defs=None, delete_all=True)

    def test_index_view_200(self):
        response = self.c.post('/flutype/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "Studies")
        self.assertContains(response, "tutorial")

    def test_antibody_view_200(self):
        response = self.c.post('/flutype/antibodies_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

        response = self.c.post('/flutype/antibodies_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

        response = self.c.post('/flutype/antibodies/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "AK_28665")

    def test_antibodybatches_view_200(self):
        response = self.c.post('/flutype/antibodybatches/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "AK025")

        response = self.c.post('/flutype/antibodybatches_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

        response = self.c.post('/flutype/antibodybatches_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

    def test_viruses_view_200(self):
        response = self.c.post('/flutype/viruses/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "A/Aichi/2/68")

        response = self.c.post('/flutype/viruses_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "A/Aichi/2/68")

        response = self.c.post('/flutype/viruses_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

    def test_virusbatches_view_200(self):
        response = self.c.post('/flutype/virusbatches/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "X31")

        response = self.c.post('/flutype/virusbatches_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "X31")

        response = self.c.post('/flutype/virusbatches_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "No entries in database")

    def test_peptides_view_200(self):
        response = self.c.post('/flutype/peptides/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "P001")

        response = self.c.post('/flutype/peptides_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "No entries in database")

        response = self.c.post('/flutype/peptides_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "P001")

    def test_peptidebatches_view_200(self):
        response = self.c.post('/flutype/peptidebatches/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "L002")

        response = self.c.post('/flutype/peptidebatches_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "No entries in database")

        response = self.c.post('/flutype/peptidebatches_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "L002")

    def test_processes_view_200(self):
        response = self.c.post('/flutype/processes/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "170509-00")

    def test_process_view_200(self):
        id = Process.objects.last().id
        response = self.c.post('/flutype/process/' + str(id) + "/", {})
        status = response.status_code

        self.assertEqual(status, 200, "view 200")

    def test_process_with_process_steps_view_200(self):
        id = Process.objects.last().id
        response = self.c.post('/flutype/process/' + str(id) + "/", {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

    def test_users_view_200(self):
        response = self.c.post('/flutype/users/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "konigmatt@googlemail.com")


    def test_rawspotcollection_view_200(self):
        id = RawSpotCollection.objects.first().id
        response = self.c.get('/flutype/measurement/' + str(id) + '/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")



