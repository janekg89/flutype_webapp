#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flutype_webapp.settings import DEFAULT_USER_PASSWORD
from django.test import TestCase, Client, TransactionTestCase, tag



from flutype.data_management.fill_users import create_users, user_defs
from flutype.data_management.fill_database import DatabaseDJ

from flutype.models import RawSpotCollection, SpotCollection, Process
from flutype.data_management.master import Master, BASEPATH, Study
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
        response = self.c.post('/about/', {})
        status = response.status_code
        self.assertEqual(status, 200, "about view 200")
        self.assertContains(response, "<h2>FluType</h2>")

    #######################################################################
    # No permission
    def test_index_view_302(self):
        response = self.c.post('/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

    def test_redirect_if_not_logged_in(self):
        response = self.c.get('/', {})
        self.assertRedirects(response, '/login/?next=/')

    def test_antibody_view_302(self):


        response = self.c.post('/antibodies/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

    def test_antibodybatches_view_302(self):
        response = self.c.post('/antibodybatches/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")



    def test_viruses_view_302(self):
        response = self.c.post('/viruses/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")



    def test_virusbatches_view_302(self):
        response = self.c.post('/virusbatches/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")


    def test_peptides_view_302(self):
        response = self.c.post('/peptides/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")


    def test_peptidebatches_view_302(self):
        response = self.c.post('/peptidebatches/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")


    def test_processes_view_302(self):
        response = self.c.post('/processes/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

    def test_users_view_302(self):
        response = self.c.post('/users/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

    def test_myexperiments_view_302(self):
        response = self.c.post('/mymeasurements/', {})
        status = response.status_code
        self.assertEqual(status, 302, "view 302")

    def test_password_view_302(self):
        response = self.c.post('/password/', {})
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
        response = self.c.post('/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "Studies")

    def test_antibody_view_200(self):


        response = self.c.post('/antibodies/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

    def test_antibodybatches_view_200(self):
        response = self.c.post('/antibodybatches/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")



    def test_viruses_view_200(self):
        response = self.c.post('/viruses/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")



    def test_virusbatches_view_200(self):
        response = self.c.post('/virusbatches/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")



    def test_peptides_view_200(self):
        response = self.c.post('/peptides/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")



    def test_peptidebatches_view_200(self):
        response = self.c.post('/peptidebatches/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")



    def test_processes_view_200(self):
        response = self.c.post('/processes/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

    def test_users_view_200(self):
        response = self.c.post('/users/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "mkoenig")

    def test_myexperiments_view_200(self):
        response = self.c.post('/mymeasurements/', {})
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
        buffer =  self.ma.read_buffer()

        self.db.update_ligands_or_batches(ligands)
        self.db.update_ligands_or_batches(complex)
        self.db.update_ligands_or_batches(buffer)


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
        response = self.c.post('/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "Studies")
        self.assertContains(response, "tutorial")

    def test_antibody_view_200(self):


        response = self.c.post('/antibodies/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "AK_28665")

    def test_antibodybatches_view_200(self):
        response = self.c.post('/antibodybatches/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "AK100")



    def test_viruses_view_200(self):
        response = self.c.post('/viruses/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "A/Aichi/2/68")



    def test_virusbatches_view_200(self):
        response = self.c.post('/virusbatches/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "X31")



    def test_peptides_view_200(self):
        response = self.c.post('/peptides/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "P001")



    def test_peptidebatches_view_200(self):
        response = self.c.post('/peptidebatches/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "P001")


    def test_processes_view_200(self):
        response = self.c.post('/processes/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "170509-00")

    def test_process_view_200(self):
        sid = Process.objects.last().sid
        response = self.c.post('/process/' + str(sid) + "/", {})
        status = response.status_code

        self.assertEqual(status, 200, "view 200")

    def test_process_with_process_steps_view_200(self):
        sid = Process.objects.last().sid
        response = self.c.post('/process/' + str(sid) + "/", {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

    def test_users_view_200(self):
        response = self.c.post('/users/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "konigmatt@googlemail.com")


    def test_rawspotcollection_view_200(self):
        sid = RawSpotCollection.objects.first().sid
        response = self.c.get('/measurement/' + str(sid) + '/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")



