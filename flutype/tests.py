# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flutype_webapp.settings import DEFAULT_USER_PASSWORD
from django.test import TestCase
from django.test import Client

from flutype.data_management.fill_users import create_users, user_defs


class ViewTestCase(TestCase):
    def setUp(self):
        # only create once
        create_users(user_defs=user_defs)

    def tearDown(self):
        create_users(user_defs=None, delete_all=True)

    def test_login_view(self):
        c = Client()
        response = c.post('/login/', {})
        status = response.status_code
        self.assertEqual(status, 200, "login view 200")
        self.assertTrue("<h1>Login</h1>" in str(response.content))

    def test_about_view(self):
        c = Client()
        response = c.post('/flutype/about/', {})
        status = response.status_code
        self.assertEqual(status, 200, "login view 200")
        self.assertTrue("<h1>FluType</h1>" in str(response.content))

    def test_index_view_302(self):
        c = Client()
        response = c.post('/flutype/', {})
        status = response.status_code
        self.assertEqual(status, 302, "index view 302")

    def test_index_view_200(self):
        c = Client()
        c.login(username='mkoenig', password=DEFAULT_USER_PASSWORD)
        response = c.post('/flutype/')
        status = response.status_code
        self.assertEqual(status, 200, "index view 200")
        self.assertTrue("<h1>Experiments</h1>" in str(response.content))
        self.assertTrue("No entries in database" in str(response.content))

    # TODO: write tests for all views