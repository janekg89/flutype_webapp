"""
Script for updating the master folder
all create_or_update_..., or write_... in class Master require data.
read functions require information what to read

procedure:
1. Initalize Master class with location of master folder:
ma = Master(path_to_master_folder)

2. Load data_tables (dic_data_table).
  dic_data_tables: a dictionary containing one of the following keys. Their values contain the corresponding data:
                           keys (data_format):     peptide          (pandas.DataFrame -> Columns: Peptide ID,	Linker,	Spacer,	Sequence,	C-terminus,	Name,	Types,	Comment)
                                                   peptide_batch    (pandas.DataFrame -> Columns: Ligand id,	Peptide ID,	Concentration [mg/ml], Buffer,	pH,	Purity (MS), Synthesized by,	Synthesization Date, Comment)
                                                   virus            (pandas.DataFrame -> Columns: Taxonomy ID, SubGroup, Country	Date, Strain Name)
                                                   virus_batch      (pandas.DataFrame -> Columns: Batch ID, Taxonomy ID, Concentration [mg/ml], Labeling, Buffer,	pH,	Active,	Passage History, Production Date, Comment)
                                                   spotting         (pandas.DataFrame -> Columns: Spotting ID, Spotting Method, Washing S ID,	Comment)
                                                   quenching        (pandas.DataFrame -> Columns: Queching ID, Quenching Method, Washing_Q_ID, Comment)
                                                   incubating       (pandas.DataFrame -> Columns: Incubating ID, Incubation Method, Washing I ID, Comment)
FIXME: Better column nameing.
FIXME: Different handling of Washing.
FIXME: Add anti_body and anti_body_batch
FIXME: Add Ligand. It can be Peptide Batch, Virus Batch, Anti_body_batch

3. write dic_data_tables to files. Any key in Datatables will create a .csv file from its value(pandas.DataFrame) in (Master_folder/data_tabels/.)
  ma.write_data_tables(data_tables_dic)
FIXME: make it possible to update data_tables and not only overwrite them.

4. Select name of collection data (convention: collection_id).

5. Load collection data (dic_data) from your desired source (e.g. fluType_analysis_folder, backup, website)
  dic_data: a dictionary containing one of the following keys. Their values contain the corresponding data:
                           keys (data_format):     gal_ligand   (pandas.DataFrame -> Columns: "Row", "Column", "Name")
                                                   gal_virus    (pandas.DataFrame -> Columns: "Row", "Column", "Name")
                                                   meta         (dictionary -> keys: Manfacturer,	HolderType,	Spotting, Incubating,	HolderBatch, SID, SurfaceSubstance, Quenching, ProcessUser)
                (optional)                         image        (cv2 image file in grayscale)
                (important for q_collection)       intensity    (pandas.DataFrame -> Columns: "Columns" Index:"Row" Value: Intenstities)
                (optional for q_collection)        std          (pandas.DataFrame -> Columns: "Columns" Index:"Row" Value: Standard deviation)
                (optional for q_collection)        q_meta       (dictionary -> keys with corresponding value go to q_meta.csv)

6. Create or update unique gal vir and lig FIXME: make this not nessecary anymore
  ma.create_or_update_unique_gal_vir(dic_data["gal_virus"])
  ma.create_or_update_unique_gal_lig(dic_data["gal_ligand"])

7. Create or update raw collection: (Convention: for microwell plate: q_collection_id = "raw", for microarray: q_collection_id = "not" ) FIXME: too complicate -> change convention: make two functions (create or update raw collection) and create or update quantified collection
   ma.create_or_update_collection(collection_id, dic_data, q_collection_id="raw", type="microwell")
or
   ma.create_or_update_collection(collection_id, dic_data, q_collection_id="not", type="microarray")

8. Create or update quantified collection:
   ma.create_or_update_collection(collection_id, dic_data, q_collection_id="your_q_collection_id",quantified_only=True, type="choose-from-'microwell'-or-'microarray'")
"""

from __future__ import print_function, absolute_import, division
import os
import sys
import cv2
import csv
import re
from flutype_analysis import utils
import pandas as pd
import numpy as np
from django.core.files import File

# TODO: meta csv should have field names in rows, i.e
# type  value

###############################################
# setup django (add current path to sys.path)
path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))

if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flutype_webapp.settings")

import django
django.setup()
###############################################
from flutype.data_management.read_flutype_analysis_db import load_procedure_data , load_db_from_formular

# fix for py3
try:
    input = raw_input
except NameError: pass

class Master(object):
    """ Class for operations on master files. """

    def __init__(self, path):
        """
        :param path: The path to the master directory

        """
        self.path = path
        self.data_tables_path = os.path.join(self.path, "data_tables")
        self.collections_path = os.path.join(self.path, "collections")
        self.unique_vir_gal_path = os.path.join(self.path, "unique_gal_virus")
        self.unique_lig_gal_path = os.path.join(self.path, "unique_gal_ligand")

    def write_data_tables(self, data_tables_dic):
        """
        saves datatables in master Folder
        :param data_tables_dic:
        :return:
        """
        if not os.path.exists( self.data_tables_path):
            os.makedirs(self.data_tables_path)

        for key in data_tables_dic:
            file_name = key + ".csv"
            file_path = os.path.join(self.data_tables_path, file_name)

            if os.path.isfile(file_path):
                user_input = input("Type yes if you really want to delete <{}>  ".format(key))
                if user_input == "yes":
                    pass
                else:
                    return
            data_tables_dic[key].to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')

    def read_data_tables(self):
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

    def create_or_update_gal_ligand(self, gal_ligand, collection_id):
        """
        saves gal ligand
        :param gal_ligand:
        :param collection_id:
        :return:
        """
        fname, _ = self.get_unique_gal_lig(gal_ligand)
        file_path = os.path.join(self.collections_path, collection_id, fname)
        gal_ligand.to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')

    def read_gal_ligand(self, collection_id, format="pd"):
        """

        :param collection_id:
        :param format: "pd": read as panadas dataFrame
                       "dj": django File ("rb")
        :return: gal_ligand, gal_ligand_name
        """
        collection_path = os.path.join(self.collections_path, collection_id)
        for fn in os.listdir(collection_path):
            result = re.search( 'lig(.*).txt', fn)
            if bool(result):
                f_name = fn
                break
        gal_lig_f = os.path.join(self.collections_path,collection_id,f_name)
        if format == "pd":
            gal_ligand = pd.read_csv(gal_lig_f, sep='\t', index_col="ID")
        elif format=="dj":
            gal_ligand = open(gal_lig_f, "rb")
        else:
            LookupError("format name wrong")
        return gal_ligand, f_name

    def create_or_update_gal_virus(self,gal_virus_data,collection_id):
        """
        saves gal_virus
        :param gal_virus_data:
        :param collection_id:
        :return:
        """
        #file_path = os.path.join(self.collections_path, collection_id, "gal_virus.csv")
        fname, _ = self.get_unique_gal_vir(gal_virus_data)
        file_path = os.path.join(self.collections_path, collection_id, fname)

        gal_virus_data.to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')

    def read_gal_virus(self, collection_id,format="pd"):
        """

        :param collection_id:
        :param format:  "pd": read as panadas dataFrame
                        "dj":  django File ("rb")
        :return: gal_virus: depending on format.
                f_name
        """
        collection_path = os.path.join(self.collections_path, collection_id)
        for fn in os.listdir(collection_path):
            result = re.search('vir(.*).txt', fn)
            if bool(result):
                f_name = fn
                break
        gal_lig_f = os.path.join(self.collections_path,collection_id,f_name)
        if format == "pd":
            gal_virus = pd.read_csv(gal_lig_f, sep='\t', index_col="ID")
        elif format == "dj":
            gal_virus= open(gal_lig_f, "rb")
        else:
            LookupError("format name wrong")
        return gal_virus, f_name

    def create_or_update_meta(self, meta, collection_id):
        """
        saves meta
        :param meta:
        :param collection_id:
        :return:
        """

        path_file = os.path.join(self.collections_path, collection_id, 'meta.csv')
        with open(path_file, 'w') as f:
            writer = csv.writer(f,delimiter="\t")
            for key , value in meta.items():
                writer.writerow([key,value])



    def read_meta(self,collection_id):
        """

        :param collection_id:
        :return: meta
        """
        path_file = os.path.join(self.collections_path, collection_id, 'meta.csv')
        with open(path_file, 'r') as f:
            reader = csv.reader(f, delimiter="\t")
            meta = dict(reader)
        return meta

    def create_or_update_image(self,image_data, collection_id):
        """

        :param image_data:
        :param collection_id:
        :return:
        """
        path_file = os.path.join(self.collections_path,collection_id,"image.jpg")
        cv2.imwrite(path_file, image_data)


    def read_image(self, collection_id, format="cv2"):
        """

        :param collection_id:
        :param format: cv2
                       dj
        :return: image: depending on format.
        """
        path_file = os.path.join(self.collections_path,collection_id,"image.jpg")
        if format == "cv2":
            return cv2.imread(path_file,0)
        elif format == "dj":
            return File(open(path_file, "rb"))


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

    def read_intensity(self,collection_id,q_collection_id):
        file_path = os.path.join(self.collections_path,  collection_id,q_collection_id, "intensity.csv")
        return pd.read_csv(file_path, sep='\t', index_col=0)



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

    def read_std(self,collection_id,q_collection_id):
        file_path = os.path.join(self.collections_path, collection_id, q_collection_id, "std.csv")
        return pd.read_csv(file_path, sep="\t", index_col=0)


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

        # creates path to collection if not yet present
        if not os.path.exists(collection_path):
            os.makedirs(collection_path)

        if type == "microarray":
            if q_collection_id == "not":
                # saves raw data
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
            if q_collection_id == "raw":
                # saves raw data
                self.create_or_update_gal_ligand(dic_data["gal_ligand"], collection_id)
                self.create_or_update_gal_virus(dic_data["gal_virus"], collection_id)
                self.create_or_update_meta(dic_data["meta"], collection_id)
                if "intensity" in dic_data:
                    if not os.path.exists(q_collection_path):
                        os.makedirs(q_collection_path)
                    self.create_or_update_intensity(dic_data["intensity"], collection_id=collection_id,
                                                    q_collection_id=q_collection_id)

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
            user_input = input("Type yes if you really want to delete {}  ".format(text))
            if user_input == "yes":
                pass
            else:
                return


    def read_raw_collection(self, collection_id):
        """
        reads data of one collection in the master folder.
        :param collection:
        :param quantified: False                         -> reads only raw collections
                           "quantified collection name"  -> reads also collection with "quantified collection name"
        :param only_quantified: reads only  quantified collection (required:queantfied ="quantified collection name")
        :return: dic_data: a dictionary containing one of the following keys. Their values contain the corresponding data:
                              keys (values):    gal_ligand   (pandas.DataFrame -> Columns: "Row", "Column", "Name")  or (Django File)
                                                gal_virus    (pandas.DataFrame -> Columns: "Row", "Column", "Name")  or (Django File)
                                                meta         (dictionary -> keys with corresponding value go to meta.csv)
                                                image        (cv2 image file in grayscale) or (Django File)
                                                intensity    (pandas.DataFrame)
                                                data         (pandas.DataFrame -> Columns: "Columns" Index:"Row" Value: Intenstities)
                                                std          (pandas.DataFrame -> Columns: "Columns" Index:"Row" Value: Standard deviation)
        """
        dic_data = {}
        dic_data["meta"]=self.read_meta(collection_id)
        dic_data["gal_ligand"] = self.read_gal_ligand(collection_id, format="dj")
        dic_data["gal_virus"] = self.read_gal_virus(collection_id, format="dj")
        # FIXME: IF dic_data["meta"][holdertype]=microarray ...
        # or think how to show and or store rawcollection/quantified colelction.
        try:
            dic_data["image"] =  self.read_image(collection_id,format="dj")
        except:
            pass
        try:
            dic_data["intensity"] = self.read_intensity(collection_id,".")
        except:
            pass
        return dic_data

    def read_dic_spots(self, collection_id):
        dic_data = {}
        dic_data["gal_ligand"] = self.read_gal_ligand(collection_id)[0]
        dic_data["gal_virus"] = self.read_gal_virus(collection_id)[0]
        dic_data["meta"] = self.read_meta(collection_id)
        return dic_data

    def read_q_collection(self,collection_id, q_collection_id):
        #FIXME: Read q_meta
        dic_data = {}
        dic_data["gal_ligand"] = self.read_gal_ligand(collection_id)[0]
        dic_data["gal_virus"] = self.read_gal_virus(collection_id)[0]
        dic_data["meta"] = self.read_meta(collection_id)
        dic_data["intensity"] = self.read_intensity(collection_id,q_collection_id)
        try:
            dic_data["std"] = self.read_std(collection_id,q_collection_id)
        except:
            pass
        return dic_data

    def read_all_q_collection_ids_for_collection(self,collection_id):
        collection_path = os.path.join(self.collections_path,collection_id)
        q_collections = next(os.walk(collection_path))[1]
        return q_collections



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
        # search if any file in unique_lig_gal_path matches 'lig(.*).txt'.
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

    def get_unique_gal_lig(self,gal_lig):
        for fn in os.listdir(self.unique_lig_gal_path):
            file_path = os.path.join(self.unique_lig_gal_path, fn)
            # reads the matching file
            gal_ligand_master = pd.read_csv(file_path, sep='\t', index_col="ID")
            if gal_lig.equals(gal_ligand_master):
                fname = fn
                fpath = os.path.join(self.unique_lig_gal_path, fname)
                return fname, fpath
        return IOError("unique_gal_lig not found")

    def get_unique_gal_vir(self, gal_vir):
        for fn in os.listdir(self.unique_vir_gal_path):
            file_path = os.path.join(self.unique_vir_gal_path, fn)
            # reads the matching file
            gal_virus_master = pd.read_csv(file_path, sep='\t', index_col="ID")
            if gal_vir.equals(gal_virus_master):
                fname = fn
                fpath = os.path.join(self.unique_lig_gal_path, fname)
                return fname, fpath
        return IOError("unique_gal_lig not found")

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


####################################################################
if __name__ == "__main__":
    # path to the master folder
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

    # fill master/data_tables
    path_formular_db = "media/forumular_db/"
    # loads data tabels information from formular
    data_tables_dic = load_db_from_formular(path_formular_db)
    # saves data tables
    ma.write_data_tables(data_tables_dic)

    # read microarrays
    for collection_id in microarray_collection_ids:
        # loading gal_vi,gal_pep, picture,data, data_std
        dic_data = utils.load_data(collection_id, PATTERN_DIR_MICROARRAY.format(collection_id))

        # renaming keys
        dic_data = rename_dic(dic_data)

        # loading procedure data from formular
        dic_data["meta"] = load_procedure_data(PATTERN_DIR_MICROARRAY.format(collection_id))

        # get_or_create_unique_ligand / unique_virus .
        # important !!!! unique_gal_vir must be created before creating collection !!!!!
        ma.create_or_update_unique_gal_vir(dic_data["gal_virus"])
        ma.create_or_update_unique_gal_lig(dic_data["gal_ligand"])

        # saving microarray collection data
        ma.create_or_update_collection(collection_id, dic_data, q_collection_id="q001", quantified_only=False, type="microarray")

    # Read microwells
    for collection_id in microwell_collection_ids:
        # loading gal_vi,gal_pep, picture,data, data_std
        dic_data = utils.load_data(collection_id, PATTERN_DIR_MICROWELL.format(collection_id))
        # renaming keys
        dic_data = rename_dic(dic_data)
        # loading procedure data from formular
        dic_data["meta"] = load_procedure_data(PATTERN_DIR_MICROWELL.format(collection_id))
        # get_or_create_unique_ligand / unique_virus .
        # important !!!! unique_gal_vir must be created before creating collection !!!!!
        ma.create_or_update_unique_gal_vir(dic_data["gal_virus"])
        ma.create_or_update_unique_gal_lig(dic_data["gal_ligand"])

        # saving microwell plate collection data
        ma.create_or_update_collection(collection_id, dic_data, q_collection_id = "raw",
                                                                    quantified_only=False, type="microwell")
