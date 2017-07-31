from __future__ import print_function, absolute_import, division

import os
import sys
import cv2
import csv
import re
from flutype_analysis import utils, analysis
import pandas as pd
import numpy as np
# setup django (add current path to sys.path)
path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))

if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flutype_webapp.settings")

import django

django.setup()
from flutype.data_management.read_flutype_analysis_db import load_procedure_data , load_db_from_formular



# fixme: get or create to update_or_create()
class Master(object):

    def __init__(self, path):

        """
        :param path: The path to the Master Directory

        """
        self.path = path
        self.data_tables_path = os.path.join(self.path,"data_tables")
        self.collections_path = os.path.join(self.path,"collections")
        self.unique_vir_gal_path = os.path.join(self.path,"unique_gal_virus")
        self.unique_lig_gal_path = os.path.join(self.path,"unique_gal_ligand")




    def write_data_tables(self, data_tables_dic):
        """
        saves datatables
        :param data_tables_dic:
        :return:
        """

        if not os.path.exists( self.data_tables_path):
            os.makedirs(self.data_tables_path)

        for key in data_tables_dic:
            file_name = key + ".csv"
            file_path = os.path.join(self.data_tables_path,file_name)
            if os.path.isfile(file_path):
                user_input = raw_input("Type yes if you really want to delete <{}>  ".format(key))
                if user_input == "yes":
                    pass
                else:
                    return
            data_tables_dic[key].to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')






    def create_or_update_gal_ligand(self,gal_ligand_data,collection_id):
        """
        saves gal ligand
        :param gal_ligand_data:
        :param collection_id:
        :return:
        """

        file_path = os.path.join(self.collections_path, collection_id, "gal_ligand.csv")
        gal_ligand_data.to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')


    def create_or_update_gal_virus(self,gal_virus_data,collection_id):
        """
        saves gal_virus
        :param gal_virus_data:
        :param collection_id:
        :return:
        """

        file_path = os.path.join(self.collections_path, collection_id, "gal_virus.csv")
        gal_virus_data.to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')


    def create_or_update_meta(self,meta_data,collection_id):
        """
        saves meta data
        :param meta_data:
        :param collection_id:
        :return:
        """

        path_file = os.path.join(self.collections_path, collection_id, 'meta.csv')
        with open(path_file, 'wb') as f:
            w = csv.DictWriter(f, meta_data.keys(), delimiter="\t")
            w.writeheader()
            w.writerow(meta_data)

    def create_or_update_image(self,image_data, collection_id):
        path_file = os.path.join(self.collections_path,collection_id,"image.jpg")
        cv2.imwrite(path_file, image_data)

    def create_or_update_intensity(self, intensity_data, collection_id,q_collection_id):
        """
        saves intensity
        :param intensity_data:
        :param collection_id:
        :param q_collection_id:
        :return:
        """

        file_path = os.path.join(self.collections_path,  collection_id,q_collection_id, "intensity.csv")
        intensity_data.to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')

    def create_or_update_std(self, std_data, collection_id,q_collection_id):
        """
        saves std
        :param std_data:
        :param collection_id:
        :param q_collection_id:
        :return:
        """

        file_path = os.path.join(self.collections_path, collection_id,q_collection_id, "std.csv")
        std_data.to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')



    def create_or_update_collection(self, collection_id, dic_data, q_collection_id="not", quantified_only=False, type="microarray"):

        """
        The method is updating the desired data in the collection folder of one collection. The keys corresond to the specific data, which shell by updated.
        :param  collection_id: collection sid
        :param  dic_data: a dictionary containing one of the following keys. Their values contain the corresponding data:
                            keys (data_format):     gal_ligand   (pandas.DataFrame -> Columns: "Row", "Column", "Name")
                                                    gal_virus    (pandas.DataFrame -> Columns: "Row", "Column", "Name")
                                                    meta         (dictionary -> keys with corresponding value go to meta.csv)
                                                    image        (cv2 image file in grayscale)
                                                    intensity    (pandas.DataFrame -> Columns: "Columns" Index:"Row" Value: Intenstities)
                                                    std          (pandas.DataFrame -> Columns: "Columns" Index:"Row" Value: Standard deviation)
                                                    q_meta       (dictionary -> keys with corresponding value go to q_meta.csv)
        :param  q_collection_id: "not" -> Only raw data is updated. The following keys are taken into cosiderations:
                                                          (for Microarrays: gal_ligand, gal_virus, meta, image)
                                                          (for Microwell plate: gal_ligand, gal_virus, meta, image)
                              "quantified_collection_name" ->  An extra folder with "quantified_collection_name" is generated with
                                                            (std, data, q_meta)
        :param type : "microarray" or "microwell"
        :param quantified_only: raw collections are not created_or_updated

        :return:
        """

        collection_path = os.path.join(self.collections_path,collection_id)
        q_collection_path = os.path.join(collection_path, q_collection_id)

        #creates path to collection if not yet present
        if not os.path.exists(collection_path):
            os.makedirs(collection_path)

        if type == "microarray":
            if q_collection_id == "not":
                #saves raw data
                self.create_or_update_gal_ligand(dic_data["gal_ligand"], collection_id)
                self.create_or_update_gal_virus(dic_data["gal_virus"], collection_id)
                self.create_or_update_meta(dic_data["meta"], collection_id)
                self.create_or_update_image(dic_data["image"], collection_id)
                self.create_or_update_intensity(dic_data["intensity"], collection_id=collection_id, q_collection_id=q_collection_id)

            elif quantified_only:

                # creates path to quantified collection if not yet present
                if not os.path.exists(q_collection_path):
                    os.makedirs(q_collection_path)

                # saves quantified data
                self.create_or_update_intensity(dic_data["intensity"], collection_id=collection_id, q_collection_id=q_collection_id)
                if "std" in dic_data:
                    self.create_or_update_std(dic_data["std"], collection_id=collection_id, q_collection_id=q_collection_id)

            else:
                # saves raw and quantified data
                self.create_or_update_gal_ligand(dic_data["gal_ligand"], collection_id)
                self.create_or_update_gal_virus(dic_data["gal_virus"], collection_id)
                self.create_or_update_meta(dic_data["meta"], collection_id)

                if "image" in dic_data:
                    self.create_or_update_image(dic_data["image"], collection_id)
                if "intensity" in dic_data:
                    # creates path to quantified collection if not yet present
                    if not os.path.exists(q_collection_path):
                        os.makedirs(q_collection_path)
                    self.create_or_update_intensity(dic_data["intensity"], collection_id=collection_id, q_collection_id=q_collection_id)
                if "std" in dic_data:
                    self.create_or_update_std(dic_data["std"], collection_id=collection_id, q_collection_id=q_collection_id)

        elif type == "microwell":

            if q_collection_id == "not":
                #saves raw data
                self.create_or_update_gal_ligand(dic_data["gal_ligand"], collection_id)
                self.create_or_update_gal_virus(dic_data["gal_virus"], collection_id)
                self.create_or_update_meta(dic_data["meta"], collection_id)
                if "intensity" in dic_data:
                    self.create_or_update_intensity(dic_data["intensity"], collection_id=collection_id,
                                                    q_collection_id=".")

        elif quantified_only:
            # creates path to quantified collection if not yet present
            if not os.path.exists(q_collection_path):
                os.makedirs(q_collection_path)


            self.create_or_update_intensity(dic_data["intensity"], collection_id=collection_id,
                                            q_collection_id=q_collection_id)
            if "std" in dic_data:
                self.create_or_update_std(dic_data["std"], collection_id=collection_id, q_collection_id=q_collection_id)








    def flush_collection(self, collection, quantified=False ,only_quantified=False, user_input=True):

        """
        All data in Master folder will be deleted.

        :param collection: collection sid

        :param only_quantified:
        :param user_input: if False the user does not need to input yes for the command.
        :return:
        """


        if user_input:
            if only_quantified:
                text = "the quantified collections of raw collection <{}>".format(collection)
            else:
                text = "the <{}> raw collection"
            user_input = raw_input("Type yes if you really want to delete {}  ".format(text))
            if user_input == "yes":
                pass
            else:
                return



    def read_collection(self,collection):
        """
        reads data of one collection in the master folder.
        :param collection:
        :param quantified: False                         -> reads only raw collections
                           "quantified collection name"  -> reads also collection with "quantified collection name"
        :param only_quantified: reads only  quantified collection (required:queantfied ="quantified collection name")
        :return: dic_data: a dictionary containing one of the following keys. Their values contain the corresponding data:
                              keys (values):    gal_ligand   (pandas.DataFrame -> Columns: "Row", "Column", "Name")
                                                gal_virus    (pandas.DataFrame -> Columns: "Row", "Column", "Name")
                                                meta         (dictionary -> keys with corresponding value go to meta.csv)
                                                image        (cv2 image file in grayscale)
                                                data         (pandas.DataFrame -> Columns: "Columns" Index:"Row" Value: Intenstities)
                                                std          (pandas.DataFrame -> Columns: "Columns" Index:"Row" Value: Standard deviation)
        """
        #collections = next(os.walk(self.collection_path))[1]

    def read_q_collection(self,collection_id, q_collection_id):
        return dic_data


    def read_datatables(self):
        """

        :return: data_tables_dic
        """
        data_tables_dic ={}
        for fn in os.listdir(self.data_tables_path):
            key = re.search('(.*).csv', fn)
            d_file = os.path.join(self.data_tables_path,fn)
            data_tables_dic[key.group(1)] = pd.read_csv(d_file, sep="\t", encoding='utf-8')
            data_tables_dic[key.group(1)].replace([np.NaN], [None] , inplace=True)

        return data_tables_dic




    def create_or_update_unique_gal_lig(self, gal_lig):
        """

        :param gal_lig: pandas.DataFrame -> Columns: "Row", "Column", "Name"
        :return:
        """
        # creates path to collection if not yet present
        if not os.path.exists(self.unique_lig_gal_path):
            os.makedirs(self.unique_lig_gal_path)

        max_name = 0
        created = False
        #search if any file in unique_lig_gal_path matches 'lig(.*).txt'.
        for fn in os.listdir(self.unique_lig_gal_path):
            result = re.search('lig(.*).txt', fn)
            if int(result.group(1)) > max_name:
                max_name = int(result.group(1))

            file_path = os.path.join(self.unique_lig_gal_path, fn)
            # reads the matching file
            gal_ligand_master = pd.read_csv(file_path, sep='\t', index_col="ID")

            if gal_lig.equals(gal_ligand_master):
                # if file in directory equal to file delivered do not create
                fname = fn
                fpath = os.path.join(self.unique_lig_gal_path, fname)
                break
        else:
            #else: create  a new file
            created = True
            fname = 'lig' + '{:03}'.format(max_name + 1) + '.txt'
            fpath = os.path.join(self.unique_lig_gal_path, fname)
            gal_lig.to_csv(fpath, sep='\t')
        return fname, fpath, created


    def create_or_update_unique_gal_vir(self, gal_vir):
        """
        :param gal_vir: pandas.DataFrame -> Columns: "Row", "Column", "Name"
        :return:
        """
        # creates path to collection if not yet present
        if not os.path.exists(self.unique_vir_gal_path):
            os.makedirs(self.unique_vir_gal_path)

        max_name = 0
        created = False
        for fn in os.listdir(self.unique_vir_gal_path):
            result = re.search('vir(.*).txt', fn)
            if int(result.group(1)) > max_name:
                max_name = int(result.group(1))

            file_path = os.path.join(self.unique_vir_gal_path, fn)
            gal_vir_master = pd.read_csv(file_path, sep='\t', index_col="ID")
            if gal_vir.equals(gal_vir_master):
                fname = fn
                fpath = os.path.join(self.unique_vir_gal_path, fname)
                break
        else:
            created = True
            fname = 'vir' + '{:03}'.format(max_name + 1) + '.txt'
            fpath = os.path.join(self.unique_vir_gal_path, fname)
            gal_vir.to_csv(fpath, sep='\t')

        return fname, fpath, created





if __name__ == "__main__":



    # the path to the master folder
    path_master = "master/"
    ma = Master(path_master)


    ################# fill master/collections ######################
    PATTERN_DIR_MICROARRAY = "../flutype_analysis/data/{}"
    PATTERN_DIR_MICROWELL = "../flutype_analysis/data/MTP/{}"


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

    def rename_dic(dic_data):
        """
        The dictionary in which is returned  from utils.load_data has different key naming than the once needed for dic_data in
        method create_or_update_collection. rename_dic changes key names.


        :param dic_data:
        :return: dic_data: same values as before, different key names.
        """
        dic_data["gal_virus"] = dic_data.pop("gal_vir")
        dic_data["gal_ligand"] = dic_data.pop("gal_pep")
        if "tif" in dic_data:
            dic_data["image"] = dic_data.pop("tif")
        if "data" in dic_data:
            dic_data["intensity"] = dic_data.pop("data")
        elif "data_std" in dic_data:
            dic_data["std"] = dic_data.pop("data_std")
        return dic_data


    for collection_id in microarray_collection_ids:

        print(os.path.abspath(PATTERN_DIR_MICROARRAY.format(collection_id)))

        #loading gal_vi,gal_pep, picture,data, data_std
        dic_data = utils.load_data(collection_id, PATTERN_DIR_MICROARRAY.format(collection_id))
        #renaming keys
        dic_data = rename_dic(dic_data)
        #loading procedure data from formular
        dic_data["meta"] = load_procedure_data(PATTERN_DIR_MICROARRAY.format(collection_id))
        # saving microarray collection data
        ma.create_or_update_collection(collection_id, dic_data, q_collection_id="q001", quantified_only=False, type="microarray")
        # get_or_create_unique_ligand / unique_virus .
        ma.create_or_update_unique_gal_vir(dic_data["gal_virus"])
        ma.create_or_update_unique_gal_lig(dic_data["gal_ligand"])


    for collection_id in microwell_collection_ids:

        #loading gal_vi,gal_pep, picture,data, data_std
        dic_data = utils.load_data(collection_id, PATTERN_DIR_MICROWELL.format(collection_id))
        #renaming keys
        dic_data = rename_dic(dic_data)
        #loading procedure data from formular
        dic_data["meta"] = load_procedure_data(PATTERN_DIR_MICROWELL.format(collection_id))
        ######## saving microwell plate collection data
        ma.create_or_update_collection(collection_id, dic_data, q_collection_id = "not",
                                                                    quantified_only=False, type="microwell")

        # get_or_create_unique_ligand / unique_virus .
        ma.create_or_update_unique_gal_vir(dic_data["gal_virus"])
        ma.create_or_update_unique_gal_lig(dic_data["gal_ligand"])


    # fill master/data_tables
    path_formular_db = "media/forumular_db/"
    #loads data tabels information from formular
    data_tables_dic = load_db_from_formular(path_formular_db)
    #saves data tables
    ma.write_data_tables(data_tables_dic)









