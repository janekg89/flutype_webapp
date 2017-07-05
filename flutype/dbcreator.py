"""
Script for creating and filling database.

Reads the data from given excel template forms.
"""
from __future__ import print_function, absolute_import, division

import os
import sys
import numpy as np
import pandas as pd
import pyexcel as pe

from flutype_analysis import utils, analysis

# setup django (add current path to sys.path)
path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flutype_webapp.settings")

import django
django.setup()

# import models
from flutype.models import (Peptide_type,
                            Peptide,
                            Peptide_batch,
                            Virus,
                            Virus_batch,
                            Buffer,
                            User,
                            Substance,
                            Holder_type,
                            Manufacturer,
                            Sample_holder,
                            Spot,
                            Spotting,
                            Quenching,
                            Incubating)


class DBCreator(object):
    """ 
    Fill the database with peptides and Viruses.
    """
    @staticmethod
    def load_peptide_data(directory):
        """
        loads peptide data from template

        :param directory:
        :return: Pandas DataFrame with peptides
        """

        f_formular = os.path.join(directory, "form_0.1.ods")

        formular = pe.get_book(file_name=f_formular, start_row=4, start_column=4)
        pep = formular["Peptide db"]
        pep.name_columns_by_row(0)
        pep_array = pep.to_array()
        pep_array = np.array(pep_array)
        peptide_data = pd.DataFrame(pep_array[1:, :], columns=pep_array[0, :])
        # replaces empty strings tith NaN and drops completely empty rows
        peptide_data.replace("", np.NaN, inplace=True)
        peptide_data.dropna(0, how="all", inplace=True)
        # replaces NaN with None -> Django Querysets take None as Null.
        peptide_data.replace([np.NaN], [None], inplace=True)
        return peptide_data

    @staticmethod
    def load_peptide_batch_data(directory):
        """ Loads peptide batch Information from template.
        :param directory:
        :return: Pandas DataFrame with peptide batches (ligands)
        """

        # read in DataFrame
        f_formular = os.path.join(directory, "form_0.1.ods")
        formular = pe.get_book(file_name=f_formular, start_row=5,row_limit=69, start_column=2)
        pep = formular["Ligand"]
        pep.name_columns_by_row(0)
        pep_array = pep.to_array()
        pep_array = np.array(pep_array)
        #replaces empty strings tith NaN and drops completely empty rows
        ligand_data = pd.DataFrame(pep_array[1:, :], columns=pep_array[0, :])

        # DataFrane processing
        # FIXME: refactor in processing function and call in all data loading
        ligand_data.replace("", np.NaN, inplace=True)
        ligand_data.replace(0, np.NaN, inplace=True)
        ligand_data.dropna(0, how="all", inplace=True)
        #replaces NaN with None -> Django Querysets take None as Null.
        ligand_data.replace([np.NaN], [None], inplace=True)
        return ligand_data

    @staticmethod
    def load_virus_batch_data(directory):
        """ Loads virus batch Information from template.
        :param directory:
        :return: Pandas DataFrame with virus batches
        """
        f_formular = os.path.join(directory, "form_0.1.ods")
        formular = pe.get_book(file_name=f_formular, start_row=4, row_limit=68, start_column=2)
        virus = formular["Influenza"]
        virus.name_columns_by_row(0)
        virus_array = virus.to_array()
        virus_array = np.array(virus_array)
        #replaces empty strings tith NaN and drops completely empty rows
        virus_array = pd.DataFrame(virus_array[1:, :], columns=virus_array[0, :])
        virus_array.replace("", np.NaN, inplace=True)
        virus_array.replace(0, np.NaN, inplace=True)
        virus_array.dropna(0, how="all", inplace=True)
        #replaces NaN with None -> Django Querysets take None as Null.
        virus_array.replace([np.NaN], [None], inplace=True)
        #change to binary format
        virus_array["Active"].replace("no", False, inplace=True)
        return virus_array


    @staticmethod
    def load_virus_data(directory):
        """ Loads virus data from template.

        :param directory:
        :return: Pandas DataFrame with virus data
        """
        f_formular = os.path.join(directory, "form_0.1.ods")
        formular = pe.get_book(file_name=f_formular, start_row=4, row_limit=68, start_column=2)
        virus = formular["Influenza db"]
        virus.name_columns_by_row(0)
        virus_array = virus.to_array()
        virus_array = np.array(virus_array)
        virus_data = pd.DataFrame(virus_array[1:, :], columns=virus_array[0, :])
        #replaces empty strings tith NaN and drops completely empty rows
        virus_data.replace("", np.NaN, inplace=True)
        virus_data.replace(0, np.NaN, inplace=True)
        virus_data.dropna(0, how="all", inplace=True)
        #replaces NaN with None -> Django Querysets take None as Null.
        virus_data.replace([np.NaN], [None], inplace=True)
        return virus_data


    @staticmethod
    def load_user_data(directory):
        """ Loads user data from template.
        :param directory:
        :return: Pandas DataFrame with user data
        """
        f_formular = os.path.join(directory, "form_0.1.ods")
        formular = pe.get_book(file_name=f_formular, start_row=3, row_limit=5, start_column=2, column_limit=1)
        name = formular["User , Washing,surface, Buffer"]
        name.name_columns_by_row(0)
        name_array = name.to_array()
        name_array = np.array(name_array)
        name_data = pd.DataFrame(name_array[1:, :], columns=name_array[0, :])
        #replaces empty strings tith NaN and drops completely empty rows
        name_data.replace("", np.NaN, inplace=True)
        name_data.replace(0, np.NaN, inplace=True)
        name_data.dropna(0, how="all", inplace=True)
        #replaces NaN with None -> Django Querysets take None as Null.
        name_data.replace([np.NaN], [None], inplace=True)
        return name_data

    @staticmethod
    def load_treatment_data(treatment,directory):
        """ Loads user data from template.
        :param directory:
        :return: Pandas DataFrame with user data
        """
        f_formular = os.path.join(directory, "form_0.1.ods")
        formular = pe.get_book(file_name=f_formular, start_row=4, start_column=2, )
        name = formular[treatment]
        name.name_columns_by_row(0)
        name_array = name.to_array()
        name_array = np.array(name_array)
        name_data = pd.DataFrame(name_array[1:, :], columns=name_array[0, :])
        # replaces empty strings tith NaN and drops completely empty rows
        name_data.replace("", np.NaN, inplace=True)
        name_data.dropna(0, how="all", inplace=True)
        # replaces NaN with None -> Django Querysets take None as Null.
        name_data.replace([np.NaN], [None], inplace=True)
        return name_data

    @staticmethod
    def load_procedure_data(directory):
        '''
        loads procedure data from template.
        :param directory:
        :return: Dictonary with process data
        '''

        f_formular = os.path.join(directory, "form_0.1.ods")
        formular = pe.get_book(file_name=f_formular, start_row=5, start_column=3)
        name = formular["Procedure"]
        name_array = name.to_array()
        name_array = np.array(name_array)
        dic_a={"S ID":name_array[0,1],"Charge":name_array[1,1],"Surface Substance":name_array[2,1],
             "manfacturer":name_array[3,1]}
        dic_b={"S ID":name_array[0,7],"Charge":name_array[1,6],"Surface Substance":name_array[2,7],
             "manfacturer":name_array[3,7]}
        if any(dic_a.values()):
            print("Sample Holder is a microarray.")
            dic_a["Holder Type"]= "microarray"
            return dic_a

        elif any(dic_b.values()):
            print("Sample Holder is a microwell plate.")
            dic_b["Holder Type"]="microwell"
            return dic_b










    @staticmethod
    def fromdata2db(directory):
        """ fills database from one form with peptides, peptide batches, viruses, virus batches, users, buffers, peptide types.
            Convention: None (Null): data not present.
                        Not for Text: data has no value.

        :param: directory: directory containing data

        :return:
        """
        print("-"*80)
        print("Filling database with fromdata2db")
        print("-" * 80)
        #loads data from template
        virus_data = DBCreator.load_virus_data(directory)
        virus_batch_data = DBCreator.load_virus_batch_data(directory)
        peptide_data = DBCreator.load_peptide_data(directory)
        peptide__batch_data = DBCreator.load_peptide_batch_data(directory)
        user_data = DBCreator.load_user_data(directory)
        spotting_data = DBCreator.load_treatment_data("Spotting",directory)
        quenching_data = DBCreator.load_treatment_data("Quenching",directory)
        incubating_data = DBCreator.load_treatment_data("Incubating",directory)



        # Stores informations if any new data was loaded.
        created_u = []
        created_l = []
        created_p = []
        created_v = []
        created_pt = []
        created_vb = []
        created_bu = []

        # fills viruses
        for k, virus in virus_data.iterrows():
            virus, created = Virus.objects.get_or_create(subgroup=virus["SubGroup"],
                                                         country=virus["Country"],
                                                         date_of_appearance=virus["Date"],
                                                         strain=virus["Strain Name"],
                                                         tax_id=virus["Taxonomy ID"]
                                                         )
            created_v.append(created)

        print("Updated any viruses in the database:", any(created_v))



        print("-" * 80)
        print("Virus batches without foreignkey to a virus in the database")
        print("-" * 80)
        for k, virus_batch in virus_batch_data.iterrows():

            try:
                # fills buffer
                Buffer_in_db, created = Buffer.objects.get_or_create(name=virus_batch["Buffer"])
                created_bu.append(created)
            except:
                Buffer_in_db = None

            created_bu.append(created)

            try:
                virus = Virus.objects.get(tax_id=virus_batch["Taxonomy ID"])
            except:
                virus = None
                #prints all virus batches without foreignkey to a virus in the database
                print(virus_batch["Batch ID"])
            #fills virus batches
            virus_batch, created = Virus_batch.objects.get_or_create(v_batch_id=virus_batch["Batch ID"],
                                                                     passage_history=virus_batch["Passage History"],
                                                                     active=virus_batch["Active"],
                                                                     labeling=virus_batch["Labeling"],
                                                                     virus=virus,
                                                                     concentration=virus_batch["Concentration [mg/ml]"],
                                                                     pH=virus_batch["pH"],
                                                                     buffer=Buffer_in_db,
                                                                     production_date=virus_batch["Production Date"],
                                                                     comment=virus_batch["Comment"]
                                                                     )
            created_vb.append(created)
        print("-" * 80)
        print("Updated any viruses batches in the database:", any(created_v))

        for k, peptide in peptide_data.iterrows():

            #fills peptide types
            pep_type , created = Peptide_type.objects.get_or_create(p_types=peptide["Types"])
            created_pt.append(created)

            #fills peptides
            peptide, created = Peptide.objects.get_or_create(id_pep=peptide["Peptide ID"],
                                                             name=peptide["Name"],
                                                             linker=peptide["Linker"],
                                                             spacer=peptide["Spacer"],
                                                             sequence=peptide["Sequence"],
                                                             c_terminus=peptide["C-terminus"],
                                                             pep_type=pep_type
                                                             )
            created_p.append(created)

        print("Updated any peptides in the database:",any(created_p))
        print("Updated any peptide types in the database:",any(created_pt))


        for k, user in user_data.iterrows():
            #fills users
            user, created = User.objects.get_or_create(name=user["User Name"])
            created_u.append(created)

        print("Updated any user in the database:",any(created_u))
        print("-" * 80)
        print("Peptide batches without foreignkey to a peptide in the database")
        print("-" * 80)

        for k, ligand in peptide__batch_data.iterrows():
            try:
                #fills buffer
                Buffer_in_db, created = Buffer.objects.get_or_create(name=ligand["Buffer"])
                created_bu.append(created)
            except:
                Buffer_in_db = None

            try:
                peptide = Peptide.objects.get(id_pep = ligand["Peptide ID"])
            except:
                peptide = None

                #prints all peptide batches without foreignkey to a virus in the database

                print(ligand["Ligand id"])

            #fills peptide_batches
            #print(ligand["Peptide ID"])
            _ , created = Peptide_batch.objects.get_or_create(p_batch_id = ligand["Ligand id"],
                                                                              peptide=peptide,
                                                                              concentration = ligand["Concentration [mg/ml]"],
                                                                              pH = ligand["pH"],
                                                                              purity = ligand["Purity (MS)"],
                                                                              buffer = Buffer_in_db,
                                                                              produced_by = ligand["Synthesized by"],
                                                                              production_date = ligand["Synthesization Date"],
                                                                              comment = ligand["Comment"]
                                                                              )

            created_l.append(created)

        print("-" * 80)
        print("Updated any buffer in the database:", any(created_bu))

        print("Updated any ligands in the database:",any(created_l))

        #_, created = Spotting.objects.get_or_create()








        print("-" * 80)
        print("Finished loading fromdata2db.")
        print("-" * 80)


    @staticmethod

    def process2db(directory, data_id):
        """
        :param directory: directory containing data
        :param data_id: id of dataset
        :return:
        """
        #loads data from datafolder
        print("-" * 80)
        print("Filling data with process2db for id <{}>".format(data_id))

        proces_dic=DBCreator.load_procedure_data(directory)
        data = utils.load_data(data_id, directory)
        ana = analysis.Analysis(data)
        spots = ana.spot
        #stick to convetion if data not present -> None
        spots["Replica"].replace([np.NaN], [None], inplace=True)
        spots["Std"].replace([np.NaN], [None], inplace=True)

        #gets or creates folder type
        holder_type, _ = Holder_type.objects.get_or_create(holder_type=proces_dic["Holder Type"])

        if not proces_dic['Surface Substance']:
            name = None
        else:
            name = proces_dic['Surface Substance']
        #gets or creates substance if filled out in form
        surf_substance, _ = Substance.objects.get_or_create(name=name)


        if not proces_dic['manfacturer']:
            name = None
        else:
            name = proces_dic['manfacturer']
        #gets or creates manufacturer if filled out in form
        manufacturer, _ = Manufacturer.objects.get_or_create(name=name)

        #gets or creates sample_holder
        sample_holder, _ = Sample_holder.objects.get_or_create(s_id=proces_dic["S ID"],
                                                               charge=proces_dic["Charge"],
                                                               holder_type=holder_type,
                                                               manufacturer=manufacturer,
                                                               functionalization=surf_substance
                                                               )
        for k, spot in spots.iterrows():



            #print(spot["Peptide"])

            #gets or creates spots
            _,_ = Spot.objects.get_or_create(peptide_batch=Peptide_batch.objects.get(p_batch_id=spot["Peptide"]),
                                             virus_batch=Virus_batch.objects.get(v_batch_id=spot["Virus"]),
                                             sample_holder=sample_holder,
                                             column=spot["Column"],
                                             row= spot["Row"],
                                             intensity=spot["Intensity"],
                                             replica=spot["Replica"],
                                             std=spot["Std"]
                                             )
        print("-" * 80)
        print("Finished filling data with process2db for id <{}>".format(data_id))
        print("-" * 80)

###################################################################################
if __name__ == "__main__":

    PATTERN_DIR_MICROARRAY = "../../flutype_analysis/data/{}/"
    PATTERN_DIR_MICROWELL = "../../flutype_analysis/data/MTP/"

    data_id = "2017-05-19_E5_X31"

    # fills database from one form with peptides, peptide batches,
    # viruses, virus batches, users, buffers, peptide types.
    DBCreator().fromdata2db(PATTERN_DIR_MICROARRAY.format(data_id))

    microarray_data_ids = ["2017-05-19_E5_X31",
              "2017-05-19_E6_untenliegend_X31",
              "2017-05-19_N5_X31",
              "2017-05-19_N6_Pan",
              "2017-05-19_N9_X31",
              "2017-05-19_N10_Pan",
              "2017-05-19_N11_Cal",
              "flutype_test"
                ]
    #fills microarrray_data
    for id in microarray_data_ids:
        DBCreator().process2db(PATTERN_DIR_MICROARRAY.format(id), id)

    microwell_data_ids = ["2017-05-12_MTP_R1"]

    #fills_microwell_data
    for id in microwell_data_ids:
        DBCreator().process2db(PATTERN_DIR_MICROWELL, id)
