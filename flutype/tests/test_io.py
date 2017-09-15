from flutype.data_management.fill_database import DBDjango, path_master, fill_database
from flutype.data_management.fill_master import Master
from flutype.data_management.fill_users import create_users, user_defs
from flutype.models import Peptide, Process, RawSpotCollection, Scanning
import shutil
import os
from pathlib import Path
import numpy as np

from django.test import TestCase

class IODataTableTestCase(TestCase):

    def setUp(self):
        self.path_master_test ="temp/test_master_01/"
        if not os.path.exists(self.path_master_test):
            os.makedirs(self.path_master_test)
        self.ma = Master(path_master)
        self.ma_test = Master(self.path_master_test)
        self.db = DBDjango()
        self.collection2_id = "2017-05-19_E5"
        self.collection1_id = "170509-00"

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

    def test_scanning_step(self):
        self.db.fill_dt(self.data_tables)
        scannings = Scanning.objects.all()
        for scan in scannings:
            db_scan_sid = scan.sid

        steps = self.ma.read_steps(self.collection2_id)
        self.assertEqual(steps["step"][0], db_scan_sid)

        steps = self.ma.read_steps(self.collection1_id)
        unique_ordering = self.db.unique_ordering(steps)
        self.assertEqual(unique_ordering, "S01-I01")



    def test_read_images(self):
        #rsc = RawSpotCollection.objects.last()
        images = self.ma.read_images(self.collection2_id)
        keys = images.keys()
        self.assertEqual(list(keys)[0], 'image.jpg')
        images = self.ma.read_images(self.collection1_id)
        self.assertFalse(bool(images))


    def test_load_data_tables_from_db(self):
        self.db.fill_dt(self.data_tables)
        datatables_loaded =self.db.load_database()

        for key in self.data_table_keys:
            self.assertTrue(set(datatables_loaded[key].keys()).issubset(self.data_tables[key]))

    def test_write_data_tables_to_master(self):
        self.db.fill_dt(self.data_tables)
        datatables_loaded = self.db.load_database()
        self.ma_test.write_data_tables(datatables_loaded)
        for key in self.data_table_keys:
            file_path = os.path.join(self.path_master_test, "data_tables","{}.csv".format(key))
            self.assertTrue(Path(file_path).is_file())

        datatables_loaded2 = self.ma_test.read_data_tables()
        for key in self.data_table_keys:
            self.assertTrue(set(datatables_loaded[key].keys()).issubset(datatables_loaded2[key]))

    def test_read_data_tables(self):
        data_tables = self.ma.read_data_tables()
        self.assertEqual(set(data_tables.keys()),set(['scanning', 'antibody_batch', 'washing', 'drying', 'virus', 'complex', 'spotting', 'virus_batch', 'peptide_batch',
                                             'complex_batch', 'peptide', 'quenching', 'antibody', 'incubating', 'blocking']))


class IOCollectionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_users(user_defs=user_defs)
        fill_database(path_master=path_master, collection_ids=[
            "170509-00","2017-05-19_E5"
        ])

    def setUp(self):
        self.collection1_id = "170509-00"
        self.collection2_id = "2017-05-19_E5"

        self.path_master_test = "temp/test_master_01/"
        if not os.path.exists(self.path_master_test):
            os.makedirs(self.path_master_test)
        self.ma = Master(path_master)
        self.ma_test = Master(self.path_master_test)
        self.db = DBDjango()
        self.data_tables = self.ma.read_data_tables()
        self.process_keys = ["id", "process", "step", "index", "user", "start", "finish", "comment"]
        self.rsc_meta_keys = ['surface_substance', 'manufacturer', 'sid', 'holder_type','holder_batch']
        self.sc_meta_keys = ["comment","image2numeric_version","processing_type"]

    def tearDown(self):
        create_users(user_defs=None, delete_all=True)
        shutil.rmtree(self.path_master_test)

    def load_process_from_db(self):
        p_db = Process.objects.first()
        process = self.db.load_process(p_db)
        print(process)
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
        data_dic_sc = self.db.load_spot_collection_from_db(sc1)
        self.assertTrue(set(["meta","intensity","std"]).issubset(data_dic_sc))

    def test_load_raw_spot_collection_from_db(self):
        rsc = RawSpotCollection.objects.first()
        data_dic_rsc = self.db.load_raw_spot_collection_from_db(rsc)
        self.assertTrue(set(["meta","gal_lig1","gal_lig2","process","images"]).issubset(data_dic_rsc))
        self.assertFalse(set(["spot_collections"]).issubset(data_dic_rsc))

    def test_load_complete_collection_from_db(self):
        rsc = RawSpotCollection.objects.first()
        data_dic_rsc = self.db.load_complete_collection_from_db(rsc)
        self.assertTrue(set(["spot_collections","meta", "gal_lig1", "gal_lig2", "process", "images"]).issubset(data_dic_rsc))

    def test_load_image(self):
        rsc = RawSpotCollection.objects.first()
        fname, image = self.db.load_scanning_images_from_db(rsc)
        self.assertFalse(bool(image))

        rsc = RawSpotCollection.objects.last()
        fname, image = self.db.load_scanning_images_from_db(rsc)
        self.assertEqual(list(image.values())[0].format, "JPEG")

    def test_write_ligand_to_master(self):
        rsc = RawSpotCollection.objects.first()

        fname1, gal_file1 = self.db.load_gal1_from_db(rsc)
        self.ma_test.create_or_update_gal_lig1(gal_file1, self.collection1_id, fname=fname1)
        file_path = os.path.join(self.ma_test.collections_path, self.collection1_id, fname1)
        self.assertTrue(Path(file_path).is_file())

        fname2, gal_file2 = self.db.load_gal2_from_db(rsc)
        self.ma_test.create_or_update_gal_lig2(gal_file2, self.collection1_id, fname=fname2)
        file_path = os.path.join(self.ma_test.collections_path, self.collection1_id, fname2)
        self.assertTrue(Path(file_path).is_file())

    def test_create_or_update_unique_gal_lig1(self):

        rsc = RawSpotCollection.objects.first()

        fname1, gal_file1 = self.db.load_gal1_from_db(rsc)
        self.ma_test.create_or_update_unique_gal_lig1(gal_file1)
        self.ma_test.create_or_update_gal_lig1(gal_file1, self.collection1_id)
        file_path = os.path.join(self.ma_test.collections_path, self.collection1_id, "lig_fix_001.txt")
        file_path_u = os.path.join(self.ma_test.unique_lig_gal_path, "lig_fix_001.txt")

        self.assertTrue(Path(file_path).is_file())
        self.assertTrue(Path(file_path_u).is_file())

        fname2, gal_file2 = self.db.load_gal2_from_db(rsc)
        self.ma_test.create_or_update_unique_gal_lig2(gal_file2)
        self.ma_test.create_or_update_gal_lig2(gal_file2, self.collection1_id)
        file_path = os.path.join(self.ma_test.collections_path, self.collection1_id, "lig_mob_001.txt")
        file_path_u = os.path.join(self.ma_test.unique_vir_gal_path, "lig_mob_001.txt")

        self.assertTrue(Path(file_path).is_file())
        self.assertTrue(Path(file_path_u).is_file())

    def test_write_rawspot_meta_to_master(self):
        rsc = RawSpotCollection.objects.last()
        meta = self.db.load_raw_spot_meta_from_db(rsc)
        self.ma_test.create_or_update_meta(meta , self.collection2_id)
        file_path = os.path.join(self.ma_test.collections_path, self.collection2_id,"meta.csv")
        self.assertTrue(Path(file_path).is_file())

    def test_write_rsc_steps_to_master(self):
        dic_process= {}
        rsc = RawSpotCollection.objects.last()
        steps = self.db.load_process(rsc.process)
        self.ma_test.write_steps(steps, self.collection2_id)
        file_path = os.path.join(self.ma_test.collections_path, self.collection2_id, "steps.csv")
        self.assertTrue(Path(file_path).is_file())

    def test_write_rsc_master(self):
        rsc = RawSpotCollection.objects.last()
        dic_data = self.db.load_raw_spot_collection_from_db(rsc)
        self.ma_test.write_rsc_to_master(self.collection2_id,dic_data)
        files = ["meta.csv","steps.csv","2017-05-19_E5image.jpg","lig_mob_001.txt","lig_fix_001.txt"]
        for file in files:
            file_path = os.path.join(self.ma_test.collections_path, self.collection2_id, file)
            print file
            self.assertTrue(Path(file_path).is_file())

    def test_write_sc_to_master(self):
        rsc = RawSpotCollection.objects.last()
        sc1 = rsc.spotcollection_set.first()
        data_dic_sc = self.db.load_spot_collection_from_db(sc1)
        self.ma_test.write_sc_to_master(self.collection2_id,"q001",data_dic_sc)
        files = ["intensity.csv", "std.csv","meta.csv"]
        for file in files:
            file_path = os.path.join(self.ma_test.collections_path,self.collection2_id,"q001",file)
            self.assertTrue(Path(file_path).is_file())

    def test_write_complete_collection_to_master_for_2_collections(self):
        rscs = RawSpotCollection.objects.all()
        sids=[]
        for rsc in rscs:
            data_dic_rsc = self.db.load_complete_collection_from_db(rsc)
            self.ma_test.write_complete_rsc_to_master(data_dic_rsc)
            sids.append(data_dic_rsc["meta"]["sid"])

        files = ["2017-05-19_E5image.jpg","meta.csv", "steps.csv", "lig_mob_001.txt", "lig_fix_001.txt"]
        for file in files[1:]:
            file_path = os.path.join(self.ma_test.collections_path,sids[0], file)
            self.assertTrue(Path(file_path).is_file())

        file_path = os.path.join(self.ma_test.collections_path, sids[0], files[0])
        self.assertFalse(Path(file_path).is_file())
        files = ["meta.csv", "steps.csv", "lig_mob_002.txt", "lig_fix_002.txt"]
        for file in files:
            file_path = os.path.join(self.ma_test.collections_path,sids[1], file)
            self.assertTrue(Path(file_path).is_file())



