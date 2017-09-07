from flutype.data_management.fill_database import Database, path_master, fill_database
from flutype.data_management.fill_master import Master
from flutype.data_management.fill_users import create_users, user_defs
from flutype.models import Peptide, Process, RawSpotCollection
import shutil
import os






from django.test import TestCase

class IODataTableTestCase(TestCase):

    def setUp(self):
        self.path_master_test ="temp/test_master_01/"
        if not os.path.exists(self.path_master_test):
            os.makedirs(self.path_master_test)
        self.ma = Master(path_master)
        self.ma_test = Master(self.path_master_test)
        self.db = Database()
        self.data_tables = self.ma.read_data_tables()
        self.data_table_keys = ['peptide',
                                 'virus',
                                 "antibody",
                                 "complex",
                                 "peptide_batch",
                                 "virus_batch",
                                 "antibody_batch",
                                 "complex_batch",
                                 "spotting",
                                 "washing",
                                 "drying",
                                 "quenching",
                                 "incubating"]

    def tearDown(self):
        shutil.rmtree(self.path_master_test)

    def test_read_data_tables_from_master(self):
        self.assertTrue(set(self.data_table_keys).issubset(self.data_tables))

    def test_fill_data_tables_to_db(self):
        self.db.fill_dt(self.data_tables)
        peptides = Peptide.objects.all()
        self.assertTrue(len(peptides) > 0)


    def test_load_data_tables_from_db(self):
        self.db.fill_dt(self.data_tables)
        datatables_loaded =self.db.load_database()

        for key in self.data_table_keys:
            self.assertTrue(set(self.data_tables[key].keys()).issubset(datatables_loaded[key]))

    def test_write_data_tables_to_master(self):
        self.db.fill_dt(self.data_tables)
        datatables_loaded = self.db.load_database()
        self.ma_test.write_data_tables(datatables_loaded)
        datatables_loaded2 = self.ma_test.read_data_tables()

        for key in self.data_table_keys:
            self.assertTrue(set(datatables_loaded[key].keys()).issubset(datatables_loaded2[key]))

class IOCollectionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_users(user_defs=user_defs)
        fill_database(path_master=path_master, collection_ids=[
            "2017-05-19_E5_X31"
        ])


    def tearDown(self):
        create_users(user_defs=None, delete_all=True)

    def setUp(self):
        self.path_master_test = "temp/test_master_01/"
        if not os.path.exists(self.path_master_test):
            os.makedirs(self.path_master_test)
        self.ma = Master(path_master)
        self.ma_test = Master(self.path_master_test)
        self.db = Database()
        self.data_tables = self.ma.read_data_tables()
        self.process_keys = ["id", "process", "step", "index", "user", "start", "finish", "comment"]
        self.rsc_meta_keys = ['surface_substance', 'manufacturer', 'sid', 'holder_type','holder_batch', 'user']

    def tearDown(self):
        shutil.rmtree(self.path_master_test)

    def load_process_from_db(self):
        p_db = Process.objects.first()
        process = self.db.load_process(p_db)
        self.assertTrue(set(self.process_keys).issubset(process))

    def load_gal_from_db(self, raw_spot_collection):
        return raw_spot_collection.image

    def test_load_raw_spot_meta_from_db(self):
        rsc = RawSpotCollection.objects.first()
        meta = self.db.load_raw_spot_meta_from_db(rsc)
        self.assertTrue(set(self.rsc_meta_keys).issubset(meta))

    def load_spot_collection_meta_from_db(self):

        pass

    def load_spot_collection_intensity_from_db(self):
        pass

    def load_image_from_db(self):
        pass

    def load_spot_collection_from_db(self):
        pass

    def load_raw_spot_collection_from_db(self):
        pass

    def load_complete_collection_from_db(self):
        pass










