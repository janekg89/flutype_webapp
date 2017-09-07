from flutype.data_management.fill_database import Database, path_master, fill_database
from flutype.data_management.fill_master import Master
from flutype.data_management.fill_users import create_users, user_defs
from flutype.models import Peptide, Process, RawSpotCollection, SpotCollection
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
            "2017-05-12_MTP_R1"
        ])


    def tearDown(self):
        create_users(user_defs=None, delete_all=True)

    def setUp(self):
        self.collection_id = "2017-05-12_MTP_R1"
        self.path_master_test = "temp/test_master_01/"
        if not os.path.exists(self.path_master_test):
            os.makedirs(self.path_master_test)
        self.ma = Master(path_master)
        self.ma_test = Master(self.path_master_test)
        self.db = Database()
        self.data_tables = self.ma.read_data_tables()
        self.process_keys = ["id", "process", "step", "index", "user", "start", "finish", "comment"]
        self.rsc_meta_keys = ['surface_substance', 'manufacturer', 'sid', 'holder_type','holder_batch', 'user']
        self.sc_meta_keys = ["comment","image2numeric_version","processing_type"]

    def tearDown(self):
        pass
        #shutil.rmtree(self.path_master_test)

    def load_process_from_db(self):
        p_db = Process.objects.first()
        process = self.db.load_process(p_db)
        self.assertTrue(set(self.process_keys).issubset(process))

    def test_load_gal_from_db(self):
        rsc = RawSpotCollection.objects.first()
        gal1_sid , gal1_file = self.db.load_gal1_from_db(rsc)
        gal2_sid , gal2_file = self.db.load_gal2_from_db(rsc)
        self.assertTrue("lig_fix_004.txt" ,gal1_sid)
        self.assertTrue("lig_mob_006.txt", gal2_sid)


    def test_load_raw_spot_meta_from_db(self):
        rsc = RawSpotCollection.objects.first()
        meta = self.db.load_raw_spot_meta_from_db(rsc)
        self.assertTrue(set(self.rsc_meta_keys).issubset(meta))

    def test_load_spot_collection_meta_from_db(self):
        rsc = RawSpotCollection.objects.first()
        sc1 = rsc.spotcollection_set.first()
        meta = self.db.load_spot_collection_meta_from_db(sc1)
        self.assertTrue(set(self.sc_meta_keys).issubset(meta))

    def test_load_spot_collection_intensity_and_std_from_db(self):
        rsc = RawSpotCollection.objects.first()
        sc1 = rsc.spotcollection_set.first()

        intensity= sc1.pivot_intensity()
        self.assertEqual(intensity.shape, (8,12))

        std = sc1.pivot_std()
        self.assertEqual(std.shape, (8, 12))


    def test_load_spot_collection_from_db(self):
        rsc = RawSpotCollection.objects.first()
        sc1 = rsc.spotcollection_set.first()
        data_dic_sc = {}
        data_dic_sc["meta"] = self.db.load_spot_collection_meta_from_db(sc1)
        data_dic_sc["intensity"] = sc1.pivot_intensity()
        data_dic_sc["std"] = sc1.pivot_std()
        self.assertTrue(set(["meta","intensity","std"]).issubset(data_dic_sc))


    def test_load_raw_spot_collection_from_db(self):
        rsc = RawSpotCollection.objects.first()
        data_dic_rsc = self.db.load_raw_spot_collection_from_db(rsc)
        self.assertTrue(set(["meta","gal_lig1","gal_lig2","process","image"]).issubset(data_dic_rsc))
        self.assertFalse(set(["spot_collections"]).issubset(data_dic_rsc))


    def test_load_complete_collection_from_db(self):
        rsc = RawSpotCollection.objects.first()
        data_dic_rsc = self.db.load_complete_collection_from_db(rsc)
        self.assertTrue(set(["spot_collections","meta", "gal_lig1", "gal_lig2", "process", "image"]).issubset(data_dic_rsc))


    #fixme: working on this
    # def test_create_or_update_gal_ligand_1(self):
    #
    #     rsc = RawSpotCollection.objects.first()
    #     _, gal_file = self.db.load_gal1_from_db(rsc)
    #     self.ma_test.create_or_update_gal_ligand(gal_file,self.collection_id)











