from flutype.data_management.fill_database import Database, path_master, fill_database
from flutype.data_management.fill_master import Master
from flutype.data_management.fill_users import create_users, user_defs
from flutype.models import Peptide, Process, RawSpotCollection, SpotCollection
import shutil
import os
from pathlib import Path






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
        for key in self.data_table_keys:
            file_path = os.path.join(self.path_master_test, "data_tables","{}.csv".format(key))
            self.assertTrue(Path(file_path).is_file())

        datatables_loaded2 = self.ma_test.read_data_tables()

        for key in self.data_table_keys:
            self.assertTrue(set(datatables_loaded[key].keys()).issubset(datatables_loaded2[key]))



class IOCollectionTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_users(user_defs=user_defs)
        fill_database(path_master=path_master, collection_ids=[
            "2017-05-12_MTP_R1","2017-05-19_E5_X31"
        ])


    def setUp(self):
        self.collection1_id = "2017-05-12_MTP_R1"
        self.collection2_id = "2017-05-19_E5_X31"

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
        create_users(user_defs=None, delete_all=True)
        shutil.rmtree(self.path_master_test)

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
        data_dic_sc = self.db.load_spot_collection_from_db(sc1)
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

    def test_load_image(self):
        rsc = RawSpotCollection.objects.first()
        fname, image = self.db.load_image_from_db(rsc)
        self.assertEqual(image, None)

        rsc = RawSpotCollection.objects.last()
        fname, image = self.db.load_image_from_db(rsc)
        self.assertEqual(image.format, "JPEG")

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




    def test_write_image_to_master(self):
        rsc = RawSpotCollection.objects.last()
        _ , image = self.db.load_image_from_db(rsc)
        self.ma_test.create_or_update_image(image,self.collection2_id)
        file_path = os.path.join(self.ma_test.collections_path, self.collection2_id,"image.jpg")
        self.assertTrue(Path(file_path).is_file())

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
        files = ["meta.csv","steps.csv","image.jpg",dic_data["gal_lig1"][0],dic_data["gal_lig2"][0]]
        for file in files:
            file_path = os.path.join(self.path_master_test, "collections", self.collection2_id, file)
            self.assertTrue(Path(file_path).is_file())

    def test_write_sc_to_master(self):
        rsc = RawSpotCollection.objects.last()
        sc1 = rsc.spotcollection_set.first()
        data_dic_sc = self.db.load_spot_collection_from_db(sc1)
        self.ma_test.create_or_update_intensity(data_dic_sc["intensity"],"test","test")
        self.ma_test.create_or_update_std(data_dic_sc["std"],"test","test")
        rel_path = os.path.join("test", "test")
        self.ma_test.create_or_update_meta(data_dic_sc["meta"],rel_path)

        files = ["intensity.csv", "std.csv","meta.csv"]
        for file in files:
            file_path = os.path.join(self.ma_test.collections_path,"test","test",file)
            self.assertTrue(Path(file_path).is_file())

    def test_write_complete_collection_to_master(self):
        pass





































