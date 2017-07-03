"""
Script for creating and filling database.
"""
from __future__ import print_function, absolute_import, division

import os
from flutype_analysis import utils
from IPython.display import display, HTML
import sys



# setup django
path = '/home/janekg89/Develop/Pycharm_Projects/flutype_webapp'
if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flutype_webapp.settings")

import django
import numpy as np
import pandas as pd
import pyexcel as pe
import math
django.setup()

from flutype.models import (Peptide_type, Peptide, Peptide_batch, Virus, Virus_batch, Batch,Buffer,User)  #import models


class DBCreator(object):
    """ 
    Fill the database with peptides and Viruses.
    """
    @staticmethod
    def load_peptide_data(directory):
        f_formular = os.path.join(directory, "form_0.1.ods")
        formular = pe.get_book(file_name=f_formular, start_row=4, start_column=4)
        pep = formular["Peptide db"]
        pep.name_columns_by_row(0)
        pep_array = pep.to_array()
        pep_array = np.array(pep_array)
        peptide_data = pd.DataFrame(pep_array[1:, :], columns=pep_array[0, :])
        peptide_data.replace("", np.NaN, inplace=True)
        peptide_data.dropna(0, how="all", inplace=True)
        peptide_data.replace([np.NaN],[None], inplace=True)

        return peptide_data
    @staticmethod
    def load_peptide_batch_data(directory):
        f_formular = os.path.join(directory, "form_0.1.ods")
        formular = pe.get_book(file_name=f_formular, start_row=5,row_limit=68, start_column=2)
        pep = formular["Ligand"]
        pep.name_columns_by_row(0)
        pep_array = pep.to_array()
        pep_array = np.array(pep_array)
        ligand_data = pd.DataFrame(pep_array[1:, :], columns=pep_array[0, :])
        ligand_data.replace("", np.NaN, inplace=True)
        ligand_data.replace(0, np.NaN, inplace=True)
        ligand_data.dropna(0, how="all", inplace=True)
        ligand_data.replace([np.NaN],[None], inplace=True)
        return ligand_data

    @staticmethod
    def load_virus_batch_data(directory):
        f_formular = os.path.join(directory, "form_0.1.ods")
        formular = pe.get_book(file_name=f_formular, start_row=4, row_limit=68, start_column=2)
        virus = formular["Influenza"]
        virus.name_columns_by_row(0)
        virus_array = virus.to_array()
        virus_array = np.array(virus_array)
        virus_array = pd.DataFrame(virus_array[1:, :], columns=virus_array[0, :])
        virus_array.replace("", np.NaN, inplace=True)
        virus_array.replace(0, np.NaN, inplace=True)
        virus_array.dropna(0, how="all", inplace=True)
        virus_array.replace([np.NaN], [None], inplace=True)
        virus_array["Active"].replace("no", False, inplace=True)

        return virus_array

    @staticmethod
    def load_virus_data(directory):
        f_formular = os.path.join(directory, "form_0.1.ods")
        formular = pe.get_book(file_name=f_formular, start_row=4, row_limit=68, start_column=2)
        virus = formular["Influenza db"]
        virus.name_columns_by_row(0)
        virus_array = virus.to_array()
        virus_array = np.array(virus_array)
        virus_data = pd.DataFrame(virus_array[1:, :], columns=virus_array[0, :])
        virus_data.replace("", np.NaN, inplace=True)
        virus_data.replace(0, np.NaN, inplace=True)
        virus_data.dropna(0, how="all", inplace=True)
        virus_data.replace([np.NaN], [None], inplace=True)

        return virus_data


    @staticmethod
    def load_user_data(directory):
        f_formular = os.path.join(directory, "form_0.1.ods")
        formular = pe.get_book(file_name=f_formular, start_row=3, row_limit=5, start_column=2, column_limit=1)
        name = formular["User , Washing,surface, Buffer"]
        name.name_columns_by_row(0)
        name_array = name.to_array()
        name_array = np.array(name_array)
        name_data = pd.DataFrame(name_array[1:, :], columns=name_array[0, :])
        name_data.replace("", np.NaN, inplace=True)
        name_data.replace(0, np.NaN, inplace=True)
        name_data.dropna(0, how="all", inplace=True)
        name_data.replace([np.NaN], [None], inplace=True)
        return name_data






    @staticmethod
    def fill_db(data_id,directory):
        """ Reads the data and fills database.

        :param: fdata: directory containing data
        
        :return:
        """

        print("-"*80)
        print("Filling database")
        print("-" * 80)


        virus_data = DBCreator.load_virus_data(directory)
        created_v =[]
        for k, virus in virus_data.iterrows():
            virus, created = Virus.objects.get_or_create(subgroup=virus["SubGroup"],
                                                         country=virus["Country"],
                                                         date_of_appearance=virus["Date"],
                                                         strain=virus["Strain Name"],
                                                         tax_id=virus["Taxonomy ID"]
                                                         )

            created_v.append(created)
        print("Updated any viruses in the database:", any(created_v))

        virus_batch_data = DBCreator.load_virus_batch_data(directory)
        created_vb = []
        created_ba =[]
        created_bu = []
        for k, virus_batch in virus_batch_data.iterrows():
            try:
                Buffer_in_db, created = Buffer.objects.get_or_create(name=virus_batch["Buffer"])
                created_bu.append(created)
            except:
                Buffer_in_db = None
            '''
            
            

            try:
                #todo: ich glaube hier ist der fehler
                
                Batch_in_db, created = Batch.objects.get_or_create(concentration=virus_batch["Concentration [mg/ml]"],
                                                                   pH=virus_batch["pH"],
                                                                   buffer=Buffer_in_db,
                                                                   production_date=virus_batch["Production Date"],
                                                                   comment=virus_batch["Comment"]
                                                                   )
            except:
                Batch_in_db = None
            '''

            created_ba.append(created)
            try:

                #todo: das macht viele null enthaltende batches problem nicht mehr unigue
                virus_batch, created = Virus_batch.objects.get_or_create(passage_history=virus_batch["Passage History"],
                                                             active=virus_batch["Active"],
                                                             labeling=virus_batch["Labeling"],
                                                             virus=Virus.objects.get(tax_id=virus_batch["Taxonomy ID"]),
                                                             batch=Batch_in_db
                                                             )
                created_vb.append(created)
            except:
                pass


        print("Updated any viruses batches in the database:", any(created_v))




        peptide_data = DBCreator.load_peptide_data(directory)
        created_p=[]
        for k, peptide in peptide_data.iterrows():
            pep_type,created = Peptide_type.objects.get_or_create(p_types=peptide["Types"])


            peptide, created = Peptide.objects.get_or_create(id_pep=peptide["Peptide ID"],
                                          name=peptide["Name"],
                                          linker=peptide["Linker"],
                                          spacer=peptide["Spacer"],
                                          sequence=peptide["Sequence"],
                                          c_terminus=peptide["C-terminus"],
                                          pep_type=pep_type
                                          )
            created_p.append(created)
        print("Updated any Peptides in the database:",any(created_p))



        user_data = DBCreator.load_user_data(directory)
        created_u=[]
        for k, user in user_data.iterrows():


            user, created = User.objects.get_or_create(name=user["User Name"])
            created_u.append(created)
        print("Updated any User in the database:",any(created_u))









        peptide__batch_data = DBCreator.load_peptide_batch_data(directory)
        created_l=[]



        for k, ligand in peptide__batch_data.iterrows():
            try:
                Buffer_in_db, created = Buffer.objects.get_or_create(name=ligand["Buffer"])
                created_bu.append(created)
            except:
                Buffer_in_db = None

            Batch_in_db, created = Batch.objects.get_or_create(concentration=ligand["Concentration [mg/ml]"],
                                                                pH=ligand["pH"],
                                                                purity=ligand["Purity (MS)"],
                                                                buffer=Buffer_in_db,
                                                                produced_by=ligand["Synthesized by"],
                                                                production_date=ligand["Synthesization Date"],
                                                                comment=ligand["Comment"]
                                                                )
            created_ba.append(created)




            try:
                Petide_batch_in_db, created = Peptide_batch.objects.get_or_create(p_batch=Batch_in_db,
                                                                                    peptide=Peptide.objects.get(id_pep=ligand["Peptide ID"])
                                                                                    )
                created_l.append(created)
            except:
                pass
        print("Updated any batches in the database:", any(created_ba))

        print("Updated any buffer in the database:", any(created_bu))

        print("Updated any ligands in the database:",any(created_l))






        #data = utils.load_data(data_id,directory)
        print("-" * 80)
        print("Finished loading database")
        print("-" * 80)




if __name__ == "__main__":

    # data
    #todo: loop through all data. But not for peptide db (the correct one is in "2017-05-19_E5_X31")
    data_id = "2017-05-19_E5_X31"
    directory = "../../flutype_analysis/data/{}/".format(data_id)


    pep_data = DBCreator().fill_db(data_id,directory)


    #a=DBCreator.load_virus_data(directory)
    #print(a["Taxonomy ID"])










