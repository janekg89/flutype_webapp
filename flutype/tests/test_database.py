import os

from flutype.data_management.master import Master, BASEPATH
from flutype.data_management.database import DatabaseDJ
from django.test import TestCase
from flutype.data_management.fill_users import create_users, user_defs
from django.apps import apps
from flutype.helper import get_unique_galfile, read_gal_file
import pandas as pd
MASTERPATH = os.path.join(BASEPATH, "master_new")



class DatabaseDJTestCase(TestCase):
    def setUp(self):
        create_users(user_defs=user_defs)
        self.ma = Master(MASTERPATH)
        self.db = DatabaseDJ(self.ma)


    def test_update_ligands(self):
        Ligand_count = {"Antibody":4, "Complex":1, "Virus":6, "Peptide":66}
        #read ligands from master
        ligands = self.ma.read_ligands()
        complex = self.ma.read_complex()
        #fill database with ligands
        self.db.update_ligands_or_batches(ligands)
        self.db.update_ligands_or_batches(complex)
        #test count
        for ligand in Ligand_count:
            Ligand = apps.get_model("flutype", ligand)
            self.assertEqual(Ligand.objects.all().count(), Ligand_count[ligand])


    def test_update_batches(self):
        Ligand_batch_count = {"AntibodyBatch":12,"BufferBatch":3, "ComplexBatch":1, "VirusBatch":64, "PeptideBatch":234}

        ligands = self.ma.read_ligands()
        complex = self.ma.read_complex()
        self.db.update_ligands_or_batches(ligands)
        self.db.update_ligands_or_batches(complex)
        ligand_batches = self.ma.read_ligand_batches()
        self.db.update_ligands_or_batches(ligand_batches)

        for ligand_batch in Ligand_batch_count:
            LigandBatch = apps.get_model("flutype", ligand_batch)
            self.assertEqual(LigandBatch.objects.all().count(), Ligand_batch_count[ligand_batch])

    def test_update_steps(self):

        steps = self.ma.read_steps()
        self.db.update_steps(steps)
        steps_count = {"Incubating":15,
                       "Blocking":1,
                       "Drying":1,
                       "IncubatingAnalyt":1,
                       "Quenching":2,
                       "Scanning":3,
                       "Spotting":5,
                       "Washing":7}
        for step in steps_count:
            Step = apps.get_model("flutype", step)
            self.assertEqual(Step.objects.all().count(), steps_count[step])

    def test_update_study(self):
        ligands = self.ma.read_ligands()
        complex = self.ma.read_complex()

        self.db.update_ligands_or_batches(ligands)
        self.db.update_ligands_or_batches(complex)

        ligand_batches = self.ma.read_ligand_batches()
        self.db.update_ligands_or_batches(ligand_batches)


        steps = self.ma.read_steps()
        self.db.update_steps(steps)

        studies= self.ma.read_studies()
        path_gal_lig = studies["170929-tutorial"]["measurements"]["170929-tutorial-microwell-1"]["results"]["final"]["intensities"]
        self.db.update_studies(studies)

        Study = apps.get_model("flutype", "Study")
        RawSpotCollection = apps.get_model("flutype", "RawSpotCollection")
        SpotCollection = apps.get_model("flutype", "SpotCollection")

        studies = Study.objects.all()
        raw_spot_collections = RawSpotCollection.objects.all()
        spot_collections = SpotCollection.objects.all()

        self.assertEqual(studies.count(), 1)
        self.assertEqual(raw_spot_collections.count(), 3)
        self.assertEqual(spot_collections.count(), 4)

        df1 = read_gal_file(path_gal_lig)
        GalFile = apps.get_model("flutype", model_name="GalFile")
        galfile = GalFile.objects.get(sid="intensity_001")
        df2 = read_gal_file(galfile.file.path)
        print(df1)
        print(df2)

    def test_get_unique(self):


        studies = self.ma.read_studies()
        path_gal_lig = studies["170929-tutorial"]["measurements"]["170929-tutorial-microwell-1"]["results"]["final"]["intensities"]
        df1 = read_gal_file(path_gal_lig)
        GalFile = apps.get_model("flutype", model_name="GalFile")
        galfile = GalFile.objects.get(sid="intensity_001")
        df2 = read_gal_file(galfile.file.path)
        print(df1)
        print(df2)

    def test_ge(self):


        gal1= read_gal_file("/home/janekg89/Develop/Pycharm_Projects/flutype_webapp/media/gal_file/intensity_001.txt")

        studies = self.ma.read_studies()
        path_gal_lig = studies["170929-tutorial"]["measurements"]["170929-tutorial-microwell-1"]["results"]["final"][
            "intensities"]
        gal3 = read_gal_file(path_gal_lig)
        #print(gal3.equals(gal1))
        #print(gal3.equals(gal1))
        print(gal1.iloc[0][2])
        print(gal3.iloc[0][2])






















