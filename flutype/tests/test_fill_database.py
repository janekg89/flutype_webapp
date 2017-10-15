import os

from flutype.data_management.master import Master, BASEPATH
from flutype.data_management.fill_database import DatabaseDJ
from django.test import TransactionTestCase
from flutype.data_management.fill_users import create_users, user_defs
from django.apps import apps
from django.test import tag

MASTERPATH = os.path.join(BASEPATH, "master_test")

class DatabaseDJTestCase(TransactionTestCase):

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

        studies = self.ma.read_studies()
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

























