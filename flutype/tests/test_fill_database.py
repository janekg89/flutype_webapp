# -*- coding: utf-8 -*-

import os

from flutype.data_management.master import Master, BASEPATH
from flutype.data_management.fill_database import DatabaseDJ
from django.test import TransactionTestCase
from flutype.data_management.fill_users import create_users, user_defs
from django.apps import apps
from django.test import tag
from flutype.helper import  read_ligands ,read_complex, read_ligand_batches, get_model_by_name, read_steps, read_buffer \
    ,get_duration_or_none, duration_to_string, cap_and_read
from django_pandas.io import read_frame


MASTERPATH = os.path.join(BASEPATH, "master_test")

class DatabaseDJTestCase(TransactionTestCase):

    def setUp(self):
        create_users(user_defs=user_defs)
        self.ma = Master(MASTERPATH)
        self.db = DatabaseDJ(self.ma)


    def test_update_ligands(self):
        Ligand_count = {"Antibody":4, "Complex":1, "Virus":19, "Peptide":151}
        #read ligands from master
        ligands = self.ma.read_ligands()
        complex = self.ma.read_complex()
        buffer = self.ma.read_buffer()

        #fill database with ligands
        self.db.update_ligands_or_batches(ligands)
        self.db.update_ligands_or_batches(complex)
        self.db.update_ligands_or_batches(buffer)

        #test count
        for ligand in Ligand_count:
            Ligand = apps.get_model("flutype", ligand)
            self.assertEqual(Ligand.objects.all().count(), Ligand_count[ligand])


    def test_update_batches(self):
        Ligand_batch_count = {"AntibodyBatch":15,"BufferBatch":6, "ComplexBatch":1, "VirusBatch":172, "PeptideBatch":242}

        ligands = self.ma.read_ligands()
        complex = self.ma.read_complex()
        buffer = self.ma.read_buffer()

        self.db.update_ligands_or_batches(ligands)
        self.db.update_ligands_or_batches(complex)
        self.db.update_ligands_or_batches(buffer)

        ligand_batches = self.ma.read_ligand_batches()
        self.db.update_ligands_or_batches(ligand_batches)

        for ligand_batch in Ligand_batch_count:
            LigandBatch = apps.get_model("flutype", ligand_batch)
            self.assertEqual(LigandBatch.objects.all().count(), Ligand_batch_count[ligand_batch])

    def test_update_steps(self):

        steps = self.ma.read_steps()
        self.db.update_steps(steps)
        steps_count = {"Incubating":17,
                       "Blocking":2,
                       "Drying":2,
                       "IncubatingAnalyt":3,
                       "Quenching":2,
                       "Scanning":4,
                       "Spotting":6,
                       "Washing":7}
        for step in steps_count:
            Step = apps.get_model("flutype", step)
            self.assertEqual(Step.objects.all().count(), steps_count[step])


    def test_update_study(self):
        ligands = self.ma.read_ligands()
        complex = self.ma.read_complex()
        buffer = self.ma.read_buffer()


        self.db.update_ligands_or_batches(ligands)
        self.db.update_ligands_or_batches(complex)
        self.db.update_ligands_or_batches(buffer)


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

    def test_read_ligand(self):
        ligands = self.ma.read_ligands()
        complex = self.ma.read_complex()
        buffer = self.ma.read_buffer()


        self.db.update_ligands_or_batches(ligands)
        self.db.update_ligands_or_batches(complex)
        self.db.update_ligands_or_batches(buffer)



        ligands1 = self.ma.ligands
        for ligand in ligands1:
            df = cap_and_read(ligand)


            self.assertTrue(ligands[ligand].equals(df.reindex(columns=ligands[ligand].columns)))
        self.assertTrue(complex["complex"].equals(read_complex()))
        self.assertTrue(buffer["buffer"].equals(read_buffer()))


    def test_read_ligand_batches(self):
        ligands = self.ma.read_ligands()
        complex = self.ma.read_complex()
        buffer = self.ma.read_buffer()

        self.db.update_ligands_or_batches(ligands)
        self.db.update_ligands_or_batches(complex)
        self.db.update_ligands_or_batches(buffer)

        ligand_batches = self.ma.read_ligand_batches()
        self.db.update_ligands_or_batches(ligand_batches)

        for ligand_batch in ligand_batches.keys():
            df = read_ligand_batches(ligand_batch)
            self.assertTrue(ligand_batches[ligand_batch]["sid"].equals(df["sid"]))
            self.assertTrue(ligand_batches[ligand_batch]["comment"].equals(df["comment"]))
            self.assertTrue(ligand_batches[ligand_batch]["buffer"].equals(df["buffer"]))
            self.assertTrue(ligand_batches[ligand_batch]["produced_by"].str.lower().equals(df["produced_by"].str.lower()))
            self.assertTrue(ligand_batches[ligand_batch]["ph"].equals(df["ph"]))
            self.assertTrue(ligand_batches[ligand_batch]["production_date"].equals(df["production_date"]))
            self.assertEqual(len(ligand_batches[ligand_batch]),len(df))
            self.assertEqual(ligand_batches[ligand_batch].keys().all(),df.keys().all())


            if ligand_batch =="bufferBatch":
                #self.assertTrue(ligand_batches[ligand_batch].equals(df))
                pass

            elif ligand_batch =="virusBatch":
                self.assertTrue(ligand_batches[ligand_batch]["active"].equals(df["active"]))
                self.assertTrue(ligand_batches[ligand_batch]["passage_history"].equals(df["passage_history"]))
                self.assertTrue(ligand_batches[ligand_batch]["ligand"].equals(df["ligand"]))
                self.assertTrue(ligand_batches[ligand_batch]["labeling"].equals(df["labeling"]))
                self.assertTrue(ligand_batches[ligand_batch]["purity"].equals(df["purity"]))
                con = ligand_batches[ligand_batch]["concentration"].astype(float)
                con2 = df["concentration"].astype(float)
                self.assertTrue(con.equals(con2))

            else:
                self.assertTrue(ligand_batches[ligand_batch]["ligand"].equals(df["ligand"]))
                self.assertTrue(ligand_batches[ligand_batch]["labeling"].equals(df["labeling"]))
                self.assertTrue(ligand_batches[ligand_batch]["purity"].equals(df["purity"]))

    def test_read_steps(self):
        steps = self.ma.read_steps()
        self.db.update_steps(steps)
        for step in steps.keys():
            df = read_steps(step)
            self.assertTrue(steps[step]["sid"].equals(df["sid"]))
            self.assertTrue(steps[step]["comment"].equals(df["comment"]))
            self.assertTrue(steps[step]["temperature"].equals(df["temperature"]))
            self.assertTrue(steps[step]["method"].equals(df["method"]))

            if "substance" in steps[step].keys():
                self.assertTrue(steps[step]["substance"].equals(df["substance"]))

    def test_duration(self):
        time_delta = "2:12:12:30"
        dt = get_duration_or_none(time_delta)
        dt2 = duration_to_string(dt)
        self.assertEqual(dt2,time_delta)

























































