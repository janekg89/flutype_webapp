# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from flutype_webapp.settings import DEFAULT_USER_PASSWORD

from django.test import LiveServerTestCase
from selenium import webdriver
from flutype.data_management.fill_users import create_users, user_defs
from flutype.data_management.fill_database import fill_database, path_master
from unittest import skip
from django.test import Client

from flutype.models import RawSpotCollection, SpotCollection, Process

class SeleniumTestCase(LiveServerTestCase):

    @classmethod
    def setUpTestData(cls):
        create_users(user_defs=user_defs)

    def setUp(self):
        self.selenium = webdriver.PhantomJS()
        create_users(user_defs=user_defs)
        fill_database(path_master=path_master, collection_ids=[
            "2017-05-19_E5_X31"
        ])

    def tearDown(self):
        self.selenium.quit()

    def test_login(self):
        expected_url='%s%s' % (self.live_server_url, '/flutype/viruses/')
        self.selenium.get(expected_url)
        self.selenium.find_element_by_id('id_username').send_keys("hmemczak")
        self.selenium.find_element_by_id('id_password').send_keys(DEFAULT_USER_PASSWORD)
        self.selenium.find_element_by_name('submit_button').click()
        self.selenium.save_screenshot('flutype/tests/screenshot.png')
        self.assertIn(expected_url, self.selenium.current_url)



    def test_virussid_links_web_database(self):
        self.test_login()
        self.selenium.get('%s%s' %(self.live_server_url,"/flutype/viruses/"))
        self.selenium.save_screenshot('flutype/tests/screenshot.png')
        self.selenium.find_element_by_link_text("387139").click()
        self.assertIn("https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=387139", self.selenium.current_url)