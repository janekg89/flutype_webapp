#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flutype_webapp.settings import DEFAULT_USER_PASSWORD
from django.test import TestCase, Client, TransactionTestCase, tag



from flutype.data_management.fill_users import create_users, user_defs
from flutype.data_management.fill_database import DatabaseDJ

from flutype.models import RawSpotCollection, SpotCollection, Process
from flutype.tests.test_fill_database import MASTERPATH
from flutype.data_management.master import Master, BASEPATH


class ViewTestCaseNoDataLogOut(TestCase):

    def setUp(self):
        # only create once
        create_users(user_defs=user_defs)
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

@tag('local')
class ViewTestCaseOneCollectionLogedIn(TransactionTestCase):
    @classmethod
    def setUpTestData(cls):
        create_users(user_defs=user_defs)


    def setUp(self):
        # only create once

        self.c = Client()
        self.c.login(username='hmemczak', password=DEFAULT_USER_PASSWORD)
        self.ma = Master(MASTERPATH)
        self.DatabaseDJ(self.ma).update_db()

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
        self.assertContains(response, "AK_28665")

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
        self.assertContains(response, "1.0_AK_28667")

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
        self.assertContains(response, "Dye001")

        response = self.c.post('/flutype/peptides_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "No entries in database")

        response = self.c.post('/flutype/peptides_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "Dye001")

    def test_peptidebatches_view_200(self):
        response = self.c.post('/flutype/peptidebatches/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "DYE100")

        response = self.c.post('/flutype/peptidebatches_mobile/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "No entries in database")

        response = self.c.post('/flutype/peptidebatches_fixed/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "DYE100")

    def test_processes_view_200(self):
        response = self.c.post('/flutype/processes/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "2017-05-19_E5")

    def test_process_view_200(self):
        id = Process.objects.last().id
        response = self.c.post('/flutype/process/' + str(id) + "/", {})
        status = response.status_code

        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "No process steps avialable for NoSteps process.")

    def test_process_with_process_steps_view_200(self):
        id = Process.objects.last().id
        response = self.c.post('/flutype/process/' + str(id) + "/", {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "Spotting")

    def test_users_view_200(self):
        response = self.c.post('/flutype/users/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "konigmatt@googlemail.com")

    def test_myexperiments_view_200(self):
        response = self.c.post('/flutype/mymeasurements/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "No entries in database")

    def test_myexperiments_view_200_one_collection(self):
        response = self.c.post('/flutype/mymeasurements/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")

    def test_rawspotcollection_view_200(self):
        id = RawSpotCollection.objects.first().id
        response = self.c.post('/flutype/rawspotcollection/' + str(id) + '/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, '<a href="/flutype/qspotcollection/1/">')
        self.assertContains(response, "<td>A/Aichi/2/68 </td>")

        id = RawSpotCollection.objects.last().id
        response = self.c.post('/flutype/rawspotcollection/' + str(id) + '/', {})
        self.assertContains(response, "No process steps available for process.")


    def test_qspotcollection_view_200(self):
        id = SpotCollection.objects.first().id
        response = self.c.post('/flutype/qspotcollection/' + str(id) + '/', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, 'href="/flutype/rawspotcollection/1/"')
        self.assertContains(response, "A001")
        self.assertContains(response, "<td>A/Aichi/2/68 </td>")

    def test_qspotcollection_data_view_200(self):
        id = SpotCollection.objects.first().id
        response = self.c.get('/flutype/qspotcollection/' + str(id) + '/data', {})
        status = response.status_code
        self.assertEqual(status, 200, "view 200")
        self.assertContains(response, "Dye001")
