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
import re
import cv2
from django.core.files import File
import warnings


from flutype_analysis import utils, analysis

# setup django (add current path to sys.path)
path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flutype_webapp.settings")

import django
django.setup()

# import models
from flutype.models import (Peptide,
                            PeptideBatch,
                            Virus,
                            VirusBatch,
                            User,
                            RawSpotCollection,
                            RawSpot,
                            Spot,
                            Spotting,
                            Quenching,
                            Incubating,
                            Process,
                            GalPeptide,
                            GalVirus,
                            SpotCollection)

#fixme: get or create to update_or_create()
class DBCreator(object):
    """ 
    Fill the database with peptides and Viruses.
    """
    @staticmethod
    def load_peptide_data(directory):
        """
        loads peptide media from template

        :param directory:
        :return: Pandas DataFrame with peptides
        """

        f_formular = os.path.join(directory, "form_0.1.ods")

        formular = pe.get_book(file_name=f_formular, start_row=4, start_column=4)
        pep = formular["Peptide"]
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
        formular = pe.get_book(file_name=f_formular, start_row=5, start_column=2)
        pep = formular["PeptideBatch"]
        pep.name_columns_by_row(0)
        pep_array = pep.to_array()
        pep_array = np.array(pep_array)
        #replaces empty strings tith NaN and drops completely empty rows
        ligand_data = pd.DataFrame(pep_array[1:, :], columns=pep_array[0, :])

        # DataFrane processing
        # FIXME: refactor in processing function and call in all media loading
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
        formular = pe.get_book(file_name=f_formular, start_row=4,  start_column=2)
        virus = formular["VirusBatch"]
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
        """ Loads virus media from template.

        :param directory:
        :return: Pandas DataFrame with virus media
        """
        f_formular = os.path.join(directory, "form_0.1.ods")
        formular = pe.get_book(file_name=f_formular, start_row=4, start_column=2)
        virus = formular["Virus"]
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
        """ Loads user media from template.
        :param directory:
        :return: Pandas DataFrame with user media
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
        """ Loads user media from template.
        :param directory:
        :return: Pandas DataFrame with user media
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
    def peptide_set(RawSpotCollection):
        """
        :return: a set of peptides which were used in RawSpotCollection
        """
        raw_spots = RawSpotCollection.rawspot_set.all()
        unique_peptide_sid = []

        for raw_spot in raw_spots:
            if raw_spot.peptide_batch.peptide.sid in unique_peptide_sid:
                pass
            else:
                unique_peptide_sid.append(raw_spot.peptide_batch.peptide.sid)


        return unique_peptide_sid

    @staticmethod
    def virus_set(RawSpotCollection):
        """
        :return: a set of viruses which were used in RawSpotCollection
        """
        raw_spots = RawSpotCollection.rawspot_set.all()
        unique_virus_sid = []

        for raw_spot in raw_spots:
            virus = raw_spot.virus_batch.virus
            if not hasattr(virus, 'sid'):
                warnings.warn("No connection between virus and virus batch for virus_batch: {}".format(raw_spot.virus_batch.sid))
            else:
                if virus.sid in unique_virus_sid:
                    pass
                else:
                    unique_virus_sid.append(raw_spot.virus_batch.virus.sid)



        return  unique_virus_sid

    @staticmethod
    def load_procedure_data(directory):
        """ Loads procedure media from template.
        :param directory:
        :return: Dictonary with process media
        """
        f_formular = os.path.join(directory, "form_0.1.ods")
        formular = pe.get_book(file_name=f_formular, start_row=5, start_column=3)
        name = formular["Procedure"]
        name_array = name.to_array()
        name_array = np.array(name_array)
        dic_all={"Spotting": name_array[9,0],"Quenching":name_array[21,0],"Incubating":name_array[33,0]}
        dic_microarray = {"S ID": name_array[0,1],"Charge":name_array[1,1],"Surface Substance":name_array[2,1],
             "manfacturer": name_array[3,1]}
        dic_microwell = {"S ID": name_array[0,7],"Charge":name_array[1,6],"Surface Substance":name_array[2,7],
             "manfacturer": name_array[3,7]}
        if any(dic_microarray.values()):
            print("Sample Holder is a microarray.")
            dic_microarray["Holder Type"]= "microarray"
            dic_microarray.update(dic_all)
            return dic_microarray

        elif any(dic_microwell.values()):
            print("Sample Holder is a microwell plate.")
            dic_microwell["Holder Type"] = "microwell"
            dic_microwell.update(dic_all)
            return dic_microwell

    @staticmethod
    def get_or_create_gal_pep(directory,data):
        max_name = 0
        created = False
        for fn in os.listdir(directory):
            result = re.search('pep(.*).txt', fn)
            if int(result.group(1)) > max_name:
                max_name = int(result.group(1))

            file_path = os.path.join(directory, fn)
            pep_gal = pd.read_csv(file_path, sep='\t', index_col="ID")

            if data["gal_pep"].equals(pep_gal):
                fname = fn
                fpath = os.path.join(directory, fname)
                break
        else:
            created = True
            fname = 'pep' + '{:03}'.format(max_name + 1) + '.txt'
            fpath = os.path.join(directory,fname)
            data["gal_pep"].to_csv(fpath, sep='\t')

        return fname,fpath, created

    @staticmethod
    def get_or_create_gal_vir(directory, data):
        max_name = 0
        created = False
        for fn in os.listdir(directory):
            result = re.search('vir(.*).txt', fn)
            if int(result.group(1)) > max_name:
                max_name = int(result.group(1))

            file_path = os.path.join(directory, fn)
            pep_gal = pd.read_csv(file_path, sep='\t', index_col="ID")

            if data["gal_vir"].equals(pep_gal):
                fname = fn
                fpath = os.path.join(directory, fname)

                break
        else:
            created = True
            fname = 'vir' + '{:03}'.format(max_name + 1) + '.txt'
            fpath = os.path.join(directory,fname)
            data["gal_vir"].to_csv(fpath, sep='\t')


        return fname,fpath, created

    @staticmethod
    def get_or_create_image(directory,data):
        PATTERN_TIF = "{}_600_100_635.jpeg"
        #Pattern_jpg =
        created = False
        for fn in os.listdir(directory):
            if fn==PATTERN_TIF.format(data["data_id"]):
                fname = fn
                fpath = os.path.join(directory, fname)
                break
        else:
            fname = PATTERN_TIF.format(data["data_id"])
            fpath = os.path.join(directory,fname)
            cv2.imwrite(fpath,data["tif"])
            created = True

        return fname, fpath, created


    @staticmethod
    def fromdata2db(directory):
        """ fills database from one form with peptides, peptide batches, viruses, virus batches, users, buffers, peptide types.
            Convention: None (Null): media not present.
                        Not for Text: media has no value.

        :param: directory: directory containing media

        :return:
        """
        print("-"*80)
        print("Filling database with fromdata2db")
        print("-" * 80)
        # loads media from template
        virus_data = DBCreator.load_virus_data(directory)
        virus_batch_data = DBCreator.load_virus_batch_data(directory)
        peptide_data = DBCreator.load_peptide_data(directory)
        peptide__batch_data = DBCreator.load_peptide_batch_data(directory)
        user_data = DBCreator.load_user_data(directory)
        spotting_data = DBCreator.load_treatment_data("Spotting", directory)
        quenching_data = DBCreator.load_treatment_data("Quenching", directory)
        incubating_data = DBCreator.load_treatment_data("Incubating", directory)

        # Stores informations if any new media was loaded.
        created_u = []
        created_l = []
        created_p = []
        created_v = []
        created_vb = []

        # fills viruses
        for k, virus in virus_data.iterrows():
            virus, created = Virus.objects.get_or_create(subgroup=virus["SubGroup"],
                                                         country=virus["Country"],
                                                         date_of_appearance=virus["Date"],
                                                         strain=virus["Strain Name"],
                                                         sid=virus["Taxonomy ID"]
                                                         )
            created_v.append(created)

        print("Updated any viruses in the database:", any(created_v))

        print("-" * 80)
        print("Virus batches without foreignkey to a virus in the database")
        print("-" * 80)
        for k, virus_batch in virus_batch_data.iterrows():
            """
              try:
                # fills buffer
                Buffer_in_db, created = Buffer.objects.get_or_create(name=virus_batch["Buffer"])
                created_bu.append(created)
            except:
                Buffer_in_db = None
            
            """
            try:
                virus = Virus.objects.get(sid=virus_batch["Taxonomy ID"])
                print("**"+virus_batch["Batch ID"])

            except:
                virus = None
                #prints all virus batches without foreignkey to a virus in the database
                print(virus_batch["Batch ID"])
            #fills virus batches
            virus_batch, created = VirusBatch.objects.get_or_create(sid=virus_batch["Batch ID"],
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
            created_vb.append(created)
        print("-" * 80)
        print("Updated any viruses batches in the database:", any(created_v))

        for k, peptide in peptide_data.iterrows():
            """
            
            
            

            #fills peptide types
            pep_type , created = PeptideType.objects.get_or_create(p_types=peptide["Types"])
            created_pt.append(created)
            """

            #fills peptides
            peptide, created = Peptide.objects.get_or_create(sid=peptide["Peptide ID"],
                                                             name=peptide["Name"],
                                                             linker=peptide["Linker"],
                                                             spacer=peptide["Spacer"],
                                                             sequence=peptide["Sequence"],
                                                             c_terminus=peptide["C-terminus"],
                                                             pep_type=peptide["Types"],
                                                             comment=peptide["Comment"]
                                                             )
            created_p.append(created)

        print("Updated any peptides in the database:",any(created_p))
        #print("Updated any peptide types in the database:",any(created_pt))

        for k, user in user_data.iterrows():
            #fills users
            user, created = User.objects.get_or_create(name=user["User Name"])
            created_u.append(created)

        print("Updated any user in the database:",any(created_u))
        print("-" * 80)





        print("Peptide batches without foreignkey to a peptide in the database")
        print("-" * 80)

        for k, ligand in peptide__batch_data.iterrows():
            """
            try:
                #fills buffer
                Buffer_in_db, created = Buffer.objects.get_or_create(name=ligand["Buffer"])
                created_bu.append(created)
            except:
                Buffer_in_db = None
            """
            try:
                peptide = Peptide.objects.get(sid = ligand["Peptide ID"])
            except:
                peptide = None

                #prints all peptide batches without foreignkey to a virus in the database

                print(ligand["Ligand id"])

            #fills peptide_batches
            #print(ligand["Peptide ID"])
            _ , created = PeptideBatch.objects.get_or_create( sid = ligand["Ligand id"],
                                                              peptide=peptide,
                                                              concentration = ligand["Concentration [mg/ml]"],
                                                              ph = ligand["pH"],
                                                              purity = ligand["Purity (MS)"],
                                                              buffer = ligand["Buffer"],
                                                              produced_by = ligand["Synthesized by"],
                                                              production_date = ligand["Synthesization Date"],
                                                              comment = ligand["Comment"]
                                                              )

            created_l.append(created)

        print("-" * 80)
        #print("Updated any buffer in the database:", any(created_bu))

        print("Updated any ligands in the database:",any(created_l))

        for k, spotting in spotting_data.iterrows():
            _, created = Spotting.objects.get_or_create(sid=spotting["Spotting ID"],
                                                        method=spotting["Spotting Method"],
                                                        date_time=None,
                                                        user=None,
                                                        comment=spotting["Comment"])

        for k, quenching in quenching_data.iterrows():
            _, created = Quenching.objects.get_or_create(sid=quenching["Queching ID"],
                                                        method=quenching["Quenching Method"],
                                                        date_time=None,
                                                        user=None,
                                                        comment=quenching["Comment"])

        for k, incubating in incubating_data.iterrows():
            _, created = Incubating.objects.get_or_create(sid=incubating["Incubating ID"],
                                                         method=incubating["Incubation Method"],
                                                         date_time=None,
                                                         user=None,
                                                         comment=incubating["Comment"])



        print("-" * 80)
        print("Finished loading fromdata2db.")
        print("-" * 80)



    @staticmethod
    def process2db(directory, data_id):
        """
        :param directory: directory containing media
        :param data_id: id of dataset
        :return:
        """
        #loads media from datafolder
        print("-" * 80)
        print("Filling media with process2db for id <{}>".format(data_id))

        proces_dic=DBCreator.load_procedure_data(directory)
        data = utils.load_data(data_id, directory)
        ana = analysis.Analysis(data)
        spots = ana.spot
        #stick to convetion if media not present -> None
        spots["Replica"].replace([np.NaN], [None], inplace=True)
        spots["Std"].replace([np.NaN], [None], inplace=True)






        try:
            spotting = Spotting.objects.get(sid=proces_dic["Spotting"])
        except:
            spotting = None
        try:
            incubating = Incubating.objects.get(sid=proces_dic["Incubating"])
        except:
            incubating = None
        try:
            quenching = Quenching.objects.get(sid=proces_dic["Quenching"])
        except:
            quenching = None

        process, _ = Process.objects.get_or_create(spotting=spotting,
                                                   incubating=incubating,
                                                   quenching=quenching)



        # checks if peptide gal file exits in directory.
        pep_path = 'db_create_buffer/gal_pep/'
        vir_path = 'db_create_buffer/gal_vir/'
        scan_path = 'db_create_buffer/scan/'

        pep_name,pep_path_true, _ = DBCreator.get_or_create_gal_pep(pep_path, data)
        try:
            galpep=GalPeptide.objects.get(sid=pep_name)
        except:
            galpep,_=GalPeptide.objects.get_or_create(sid=pep_name)
            galpep.file.save(pep_name, File(open(pep_path_true, "r")))


        vir_name,vir_path_true,_= DBCreator.get_or_create_gal_vir(vir_path, data)
        try:
            galvir=GalVirus.objects.get(sid=vir_name)
        except:
            galvir,_=GalVirus.objects.get_or_create(sid=vir_name)
            galvir.file.save(vir_name,File(open(vir_path_true,"r")))



        try:
            scan_name, scan_path_true, _ = DBCreator.get_or_create_image(scan_path, data)
        except:
            scan_name = False

        #gets or gcreates pepgal



        # gets or creates raw_spot_collection
        try:
            raw_spot_collection = RawSpotCollection.objects.get(sid=proces_dic["S ID"])
        except:
            raw_spot_collection, _ = RawSpotCollection.objects.get_or_create(sid=proces_dic["S ID"],
                                                                             batch=proces_dic["Charge"],
                                                                             holder_type=proces_dic["Holder Type"],
                                                                             functionalization=proces_dic[
                                                                                 'Surface Substance'],
                                                                             manufacturer=proces_dic['manfacturer'],
                                                                             gal_peptide=galpep,
                                                                             gal_virus=galvir,
                                                                             #image=scan_path_true,
                                                                             process=process)

            # raw_spot_collection.gal_peptide.
            if scan_name:
                raw_spot_collection.image.save(scan_name, File(open(scan_path_true, "rb")))



            if all(spots["Intensity"].notnull()) :

                spot_collection ,_ = SpotCollection.objects.get_or_create(raw_spot_collection=raw_spot_collection)





            for k, spot in spots.iterrows():
                    # print(spot["Peptide"])

                    # gets or creates spots
                raw_spot, _ = RawSpot.objects.get_or_create(peptide_batch=PeptideBatch.objects.get(sid=spot["Peptide"]),
                                                                virus_batch=VirusBatch.objects.get(sid=spot["Virus"]),
                                                                raw_spot_collection=raw_spot_collection,
                                                                column=spot["Column"],
                                                                row=spot["Row"],
                                                                replica=spot["Replica"]
                                                                )

                if all(spots["Intensity"].notnull()):
                    _, _ = Spot.objects.get_or_create(raw_spot=raw_spot,
                                                      intensity=spot["Intensity"],
                                                      std=spot["Std"],
                                                      spot_collection=spot_collection)

        print("-" * 80)
        print("Finished filling media with process2db for id <{}>".format(data_id))
        print("-" * 80)

    @staticmethod
    def fillmany2many_rawspots_peptides_viruses():
            for rsc in RawSpotCollection.objects.all():
                virus_ids = DBCreator.virus_set(rsc)
                peptide_ids = DBCreator.peptide_set(rsc)

                for virus_id in virus_ids:
                    try:
                        rsc.viruses.add(Virus.objects.get(sid=virus_id))
                    except:
                        pass
                for peptide_id in peptide_ids:
                    try:
                        rsc.peptides.add(Peptide.objects.get(sid=peptide_id))
                    except:
                        pass

###################################################################################
if __name__ == "__main__":

    # load data from formualr db:
    # fills database from one form with peptides, peptide batches,
    # viruses, virus batches, users, buffers, peptide types.
    path_formular_db = "media/forumular_db/"
    file_path = os.path.join(path, path_formular_db)

    DBCreator().fromdata2db(path_formular_db)


    # requires the flutype_analysis in same directory as flutype_webapp

    PATTERN_DIR_MICROARRAY = "../flutype_analysis/data/{}"
    PATTERN_DIR_MICROWELL = "../flutype_analysis/data/MTP/{}"





    
    
    
    microarray_data_ids = [
        "2017-05-19_E5_X31",
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

    # fills microarrray_data
    for mid in microarray_data_ids:
        #file_path = os.path.join(path, PATTERN_DIR_MICROARRAY.format(mid))
        DBCreator().process2db( PATTERN_DIR_MICROARRAY.format(mid), mid)





    microwell_data_ids = ["2017-05-12_MTP_R1",
                          "2017-06-13_MTP"
                          ]

    ## fills_microwell_data
    for mid in microwell_data_ids:
        file_path = os.path.join(path, PATTERN_DIR_MICROWELL.format(mid))
        DBCreator().process2db(PATTERN_DIR_MICROWELL.format(mid), mid)

    DBCreator().fillmany2many_rawspots_peptides_viruses()

    
    
    




