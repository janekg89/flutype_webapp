from flutype.data_management.fill_database import Database, path_master
from flutype.data_management.fill_master import Master
from flutype.models import Peptide
import shutil
import os






from django.test import TestCase

class IODataTableTestCase(TestCase):

    def setUp(self):
        self.path_master_test ="test_master_01/"
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



