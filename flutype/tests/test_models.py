from flutype.data_management.fill_database import DBDjango, path_master, fill_database
from flutype.data_management.fill_master import Master
from flutype.data_management.fill_users import create_users, user_defs
from flutype.models import Peptide, Process, RawSpotCollection
from PIL import Image

import shutil
import os
from pathlib import Path


from django.test import TestCase
class IOCollectionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_users(user_defs=user_defs)
        fill_database(path_master=path_master, collection_ids=[
            "2017-05-19_E5"
        ])


    def setUp(self):
        self.db = DBDjango()


    def tearDown(self):
        create_users(user_defs=None, delete_all=True)


    def test_image_versions(self):
        rsc = RawSpotCollection.objects.first()
        image = self.db.load_image_from_db(rsc)
        image_2 = Image.open(rsc.image_90)
        self.assertEqual(image[1].size, (2200,7200))
        self.assertEqual(image_2.size,(327, 100))







