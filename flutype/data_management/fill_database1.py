"""
Script for filling database from backup
"""
from __future__ import print_function, absolute_import, division

import os
import sys
import numpy as np
import pandas as pd
import re
import cv2
from django.core.files import File
import warnings
from flutype_analysis import utils, analysis

# setup django (add current path to sys.path)
path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))
print(path)
if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flutype_webapp.settings")

import django
django.setup()
from flutype.data_management.fill_master import Master

# import models
from flutype.models import (Peptide,
                            PeptideBatch,
                            Virus,
                            VirusBatch,
                            RawSpotCollection,
                            SpotCollection,
                            RawSpot,
                            Spot,
                            Spotting,
                            Quenching,
                            Incubating,
                            Process,
                            GalPeptide,
                            GalVirus)

class Database(object):
    """
    """
    def __init__(self):
        self.type = "sqlite"

    def create_or_update_virus(self, virus):
        vir, created = Virus.objects.get_or_create(subgroup=virus["SubGroup"],
                                                   country=virus["Country"],
                                                   date_of_appearance=virus["Date"],
                                                   strain=virus["Strain Name"],
                                                   sid=virus["Taxonomy ID"]
                                                 )
        return vir, created

    def create_or_update_virus_batch(self, virus_batch):
        try:
            virus = Virus.objects.get(sid=virus_batch["Taxonomy ID"])

        except:
            virus = None
            # prints all virus batches without foreignkey to a virus in the database
            print("No virus found for virus batch with sid:" + virus_batch["Batch ID"])

        # fills virus batches
        virus_b, created = VirusBatch.objects.get_or_create(sid=virus_batch["Batch ID"],
                                                            passage_history=virus_batch["Passage History"],
                                                            active=virus_batch["Active"],
                                                            labeling=virus_batch["Labeling"],
                                                            virus=virus,
                                                            concentration=virus_batch["Concentration [mg/ml]"],
                                                            ph=virus_batch["pH"],
                                                            buffer=virus_batch["Buffer"],
                                                            production_date=virus_batch["Production Date"],
                                                            comment=virus_batch["Comment"]
                                                            )
        return virus_b ,created

    def create_or_update_peptide(self, peptide):
        # fills peptides
        peptide, created = Peptide.objects.get_or_create(sid=peptide["Peptide ID"],
                                                         name=peptide["Name"],
                                                         linker=peptide["Linker"],
                                                         spacer=peptide["Spacer"],
                                                         sequence=peptide["Sequence"],
                                                         c_terminus=peptide["C-terminus"],
                                                         pep_type=peptide["Types"],
                                                         comment=peptide["Comment"]
                                                         )
        return peptide, created
    def create_or_update_peptide_batch(self,peptide_batch):
        try:
            peptide = Peptide.objects.get(sid=peptide_batch["Peptide ID"])

        except:
            peptide = None
            # prints all peptide batches without foreignkey to a virus in the database
            print("No peptide found for peptide batch with sid:" +peptide_batch["Ligand id"])

        # fills peptide_batches
        peptide_b, created = PeptideBatch.objects.get_or_create(sid=peptide_batch["Ligand id"],
                                                        peptide=peptide,
                                                        concentration=peptide_batch["Concentration [mg/ml]"],
                                                        ph=peptide_batch["pH"],
                                                        purity=peptide_batch["Purity (MS)"],
                                                        buffer=peptide_batch["Buffer"],
                                                        produced_by=peptide_batch["Synthesized by"],
                                                        production_date=peptide_batch["Synthesization Date"],
                                                        comment=peptide_batch["Comment"]
                                                        )
        return peptide_b, created


    def create_or_update_incubating(self, incubating):
        incub, created = Incubating.objects.get_or_create(sid=incubating["Incubating ID"],
                                                         method=incubating["Incubation Method"],
                                                         date_time=None,
                                                         user=None,
                                                         comment=incubating["Comment"])
        return incub, created



    def create_or_update_quenching(self,quenching):
        quench, created = Quenching.objects.get_or_create(sid=quenching["Queching ID"],
                                                        method=quenching["Quenching Method"],
                                                        date_time=None,
                                                        user=None,
                                                        comment=quenching["Comment"])
        return quench , created

    def create_or_update_spotting(self, spotting):
        spotti, created = Spotting.objects.get_or_create(sid=spotting["Spotting ID"],
                                                    method=spotting["Spotting Method"],
                                                    date_time=None,
                                                    user=None,
                                                    comment=spotting["Comment"])
        return spotti, created


    def fill_dt(self,data_tables):
        # Stores informations if any new media was loaded.

        created_pb = []
        created_p = []
        created_v = []
        created_vb = []
        #treatments
        created_s = []
        created_q = []
        created_i = []

        # fills viruses
        for k, virus in data_tables["virus"].iterrows():
            _ , created = self.create_or_update_virus(virus)
            created_v.append(created)


        for k, virus_batch in data_tables["virus_batch"].iterrows():
           _ , created = self.create_or_update_virus_batch(virus_batch)
           created_vb.append(created)

        for k, peptide in data_tables["peptide"].iterrows():
            _ , created = self.create_or_update_peptide(peptide)
            created_p.append(created)

        for k, peptide_batch in data_tables["peptide_batch"].iterrows():
            _ ,created = self.create_or_update_peptide_batch(peptide_batch)
            created_pb.append(created)

        for k, spotting in data_tables["spotting"].iterrows():
            _ , created = self.create_or_update_spotting(spotting)
            created_s.append(created)
        for k, quenching in data_tables["quenching"].iterrows():
            _, created = self.create_or_update_quenching(quenching)
            created_q.append(created)
        for k, incubating in data_tables["incubating"].iterrows():
            _, created = self.create_or_update_incubating(incubating)
            created_i.append(created)

        print("updates to database:")
        print ("virus:", any(created_v))
        print ("virus_batch:", any(created_vb))
        print ("peptide:", any(created_p))
        print ("peptide_batch:", any(created_pb))
        print ("spotting:", any(created_s))
        print ("quenching:", any(created_q))
        print ("incubating:", any(created_i))

    def fill_collection(self,collection):
        pass










if __name__ == "__main__":



    # the path to the master folder
    path_master = "master/"
    ma = Master(path_master)


    # all sid of microarray collections
    microarray_collection_ids = ["2017-05-19_E5_X31",
                                 "2017-05-19_E6_untenliegend_X31",
                                 "2017-05-19_N5_X31",
                                 "2017-05-19_N6_Pan",
                                 "2017-05-19_N9_X31",
                                 "2017-05-19_N10_Pan",
                                 "2017-05-19_N11_Cal",
                                 "flutype_test",
                                 "P6_170613_Cal",
                                 "P5_170612_X31",
                                 "P3_170612_X31",
                                 "2017-05-19_N7_Cal"
                                 ]
                                 
    # all sids of microwell collections
    microwell_collection_ids = ["2017-05-12_MTP_R1",
                                "2017-06-13_MTP"
                                ]

    print("-" * 80)
    print("Filling database")
    print("-" * 80)
    #loads data_tables
    data_tables = ma.read_datatables()
    db = Database()
    db.fill_dt(data_tables)


    # collections = next(os.walk(self.collection_path))[1]

