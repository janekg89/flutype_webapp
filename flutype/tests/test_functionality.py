# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from flutype_webapp.settings import DEFAULT_USER_PASSWORD
from django.test import LiveServerTestCase
from selenium import webdriver
from flutype.data_management.fill_users import create_users, user_defs
from flutype.data_management.fill_database import fill_database, path_master


from flutype.models import RawSpotCollection, SpotCollection, Process


class SeleniumTestCase(LiveServerTestCase):

    @classmethod
    def setUpTestData(cls):
        create_users(user_defs=user_defs)

    def setUp(self):
        self.driver = webdriver.PhantomJS()
        create_users(user_defs=user_defs)
        fill_database(path_master=path_master, collection_ids=[
            "2017-05-19_E5_X31"
        ])

    def tearDown(self):
        self.driver.quit()

    def login(self,expected_url):
        self.driver.get(expected_url)
        self.driver.find_element_by_id('id_username').send_keys("hmemczak")
        self.driver.find_element_by_id('id_password').send_keys(DEFAULT_USER_PASSWORD)
        self.driver.find_element_by_name('submit_button').click()

    def test_login_and_redirect(self):
        expected_url = '%s%s' % (self.live_server_url, '/flutype/viruses/')
        self.login(expected_url)
        self.assertIn(expected_url, self.driver.current_url)

    def test_virussid_links_web_database(self):
        expected_url = '%s%s' %(self.live_server_url,"/flutype/viruses/")
        self.login(expected_url)
        self.driver.find_element_by_link_text("387139").click()
        self.assertIn("https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?id=387139", self.driver.current_url)

    def test_heatmap(self):
        id = SpotCollection.objects.first().id
        expected_url = '%s%s%s' %(self.live_server_url,'/flutype/qspotcollection/', id)
        self.login(expected_url)
        # keep a watch on jQuery 'active' attribute
        WebDriverWait(self.driver, 10).until(lambda s: s.execute_script("return jQuery.active == 0"))
        # page should be stable enough now, and we can perform desired actions
        elem = WebDriverWait(self.driver, 10).until(expected_conditions.visibility_of_element_located((By.ID, 'container')))
        retval = self.driver.execute_script("return lig1",elem)
        self.assertEqual(len(retval) , 25)




    def test_barplot(self):
        id = SpotCollection.objects.first().id
        expected_url = '%s%s%s' %(self.live_server_url,'/flutype/qspotcollection/', id)
        self.login(expected_url)
        # keep a watch on jQuery 'active' attribute
        WebDriverWait(self.driver, 10).until(lambda s: s.execute_script("return jQuery.active == 0"))
        # page should be stable enough now, and we can perform desired actions
        elem = WebDriverWait(self.driver, 10).until(expected_conditions.visibility_of_element_located((By.ID, 'myDiv')))
        retval = self.driver.execute_script("return Chart(dataPlot)",elem)
        self.assertEqual(len(retval),2 )


