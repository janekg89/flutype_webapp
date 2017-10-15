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

import flutype.data_management.fill_database
from flutype.models import RawSpotCollection


###############################################

# fix for py3
try:
    input = raw_input
except NameError:
    pass


class Master(object):
    """ Class for operations on master files. """

    def __init__(self, path):
        """
        :param path: The path to the master directory

        """
        self.path = path
        self.path_study = os.path.join(self.path, "studies")
        self.data_tables_path = os.path.join(self.path, "data_tables")
        self.collections_path = os.path.join(self.path, "collections")
        self.unique_vir_gal_path = os.path.join(self.path, "unique_gal_ligand2")
        self.unique_lig_gal_path = os.path.join(self.path, "unique_gal_ligand1")

    def write_data_tables(self, data_tables_dic):
        """
        saves datatables in master Folder
        :param data_tables_dic:
        """
        if not os.path.exists(self.data_tables_path):
            os.makedirs(self.data_tables_path)

        for key in data_tables_dic:
            file_name = key + ".csv"
            file_path = os.path.join(self.data_tables_path, file_name)
            data_tables_dic[key].to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')

    def write_steps(self, steps_dic, collection_id):
        """
        saves datatables in master Folder
        :param steps_dic:
        """
        collection_path = os.path.join(self.collections_path, collection_id)
        if not os.path.exists(collection_path):
            os.makedirs(collection_path)

        file_path = os.path.join(collection_path,"steps.csv")
        steps_dic.to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')

    def read_data_tables(self):
        """
        :return: data_tables_dic
        """
        data_tables_dic = {}
        for fn in os.listdir(self.data_tables_path):
            key = re.search('(.*).csv', fn)
            d_file = os.path.join(self.data_tables_path, fn)
            data_tables_dic[key.group(1)] = pd.read_csv(d_file, sep="\t", encoding='utf-8', dtype=str)
            data_tables_dic[key.group(1)].replace([np.NaN], [None], inplace=True)
        return data_tables_dic

    def read_images(self, collection_id):
        collection_path = os.path.join(self.collections_path, collection_id)
        images = {}
        for fn in os.listdir(collection_path):
            result = re.search('(.*).jpg', fn)
            if bool(result):
                path_file = os.path.join(self.collections_path, collection_id, fn)
                images[fn]=File(open(path_file, "rb"))
        return images

    def read_steps(self, collection_id):
        file_path = os.path.join(self.collections_path, collection_id, "steps.csv")
        steps = pd.read_csv(file_path, sep="\t", encoding='utf-8')
        steps.replace([np.NaN], [None], inplace=True)
        return steps

    def create_or_update_gal_lig1(self, gal_ligand, collection_id, **kwargs):
        """
        saves gal ligand
        :param gal_ligand:
        :param collection_id:
        :return:
        """
        if "fname" not in kwargs:

            kwargs["fname"] , _ = self.get_unique_gal_lig1(gal_ligand)
        collection_path = os.path.join(self.collections_path, collection_id)
        file_path = os.path.join(self.collections_path, collection_id, kwargs["fname"])
        if not os.path.exists(collection_path):
            os.makedirs(collection_path)
        gal_ligand.to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')

    def create_or_update_gal_lig2(self, gal_ligand, collection_id, **kwargs ):
        """
        saves gal ligand
        :param gal_ligand:
        :param collection_id:
        :return:
        """
        if "fname" not in kwargs:

            kwargs["fname"] , _ = self.get_unique_gal_lig2(gal_ligand)
        collection_path = os.path.join(self.collections_path, collection_id)
        file_path = os.path.join(self.collections_path, collection_id, kwargs["fname"])
        if not os.path.exists(collection_path):
            os.makedirs(collection_path)
        gal_ligand.to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')


    def read_gal_ligand(self, collection_id, format="pd", index=True):
        """
        :param collection_id:
        :param format: "pd": read as panadas dataFrame
                       "dj": django File ("rb")
        :return: gal_ligand, gal_ligand_name
        """
        collection_path = os.path.join(self.collections_path, collection_id)
        for fn in os.listdir(collection_path):
            result = re.search('lig_fix_(.*).txt', fn)
            if bool(result):
                f_name = fn
                break
        gal_lig_f = os.path.join(self.collections_path, collection_id, f_name)
        print(gal_lig_f)
        if format == "pd":
            if index:
                gal_ligand = pd.read_csv(gal_lig_f, sep='\t', index_col="ID")
            else:
                gal_ligand = pd.read_csv(gal_lig_f, sep='\t')

        elif format == "dj":
            gal_ligand = open(gal_lig_f, "rb")
        else:
            LookupError("format name wrong")
        return gal_ligand, f_name

    def create_or_update_gal_virus(self, gal_virus_data, collection_id):
        """
        saves gal_virus
        :param gal_virus_data:
        :param collection_id:
        :return:
        """
        # file_path = os.path.join(self.collections_path, collection_id, "gal_virus.csv")
        fname, _ = self.get_unique_gal_lig2(gal_virus_data)
        file_path = os.path.join(self.collections_path, collection_id, fname)

        gal_virus_data.to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')

    def read_gal_virus(self, collection_id, format="pd"):
        """

        :param collection_id:
        :param format:  "pd": read as panadas dataFrame
                        "dj":  django File ("rb")
        :return: gal_virus: depending on format.
                f_name
        """
        collection_path = os.path.join(self.collections_path, collection_id)
        for fn in os.listdir(collection_path):
            result = re.search('lig_mob_(.*).txt', fn)
            if bool(result):
                f_name = fn
                break
        gal_lig_f = os.path.join(self.collections_path, collection_id, f_name)
        if format == "pd":
            gal_virus = pd.read_csv(gal_lig_f, sep='\t', index_col="ID")
        elif format == "dj":
            gal_virus = open(gal_lig_f, "rb")
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
        collection_path = os.path.join(self.collections_path, collection_id)
        if not os.path.exists(collection_path):
            os.makedirs(collection_path)
        with open(path_file, 'w') as f:
            writer = csv.writer(f, delimiter="\t")
            for key, value in meta.items():
                writer.writerow([key, value])


    def read_meta(self, collection_id):
        """

        :param collection_id:
        :return: meta
        """
        path_file = os.path.join(self.collections_path, collection_id, 'meta.csv')
        with open(path_file, 'r') as f:
            reader = csv.reader(f, delimiter="\t")
            meta = dict(reader)
        return meta

    def create_or_update_image(self, image_data, collection_id,fname):
        """

        :param image_data:
        :param collection_id:
        :return:
        """
        path_file = os.path.join(self.collections_path, collection_id, fname)
        collection_path = os.path.join(self.collections_path, collection_id)
        if not os.path.exists(collection_path):
            os.makedirs(collection_path)
        if image_data == None:
            pass
        else:
            image_data.save(path_file)


    def create_or_update_images(self, images_data, collection_id):
        if bool(images_data):
            for image_name in images_data.keys():
                #if collection_id in image_name:
                self.create_or_update_image(images_data[image_name],collection_id,image_name)


    def read_image(self, collection_id, format="cv2"):
        """

        :param collection_id:
        :param format: cv2
                       dj
        :return: image: depending on format.
        """
        path_file = os.path.join(self.collections_path, collection_id, "image.jpg")
        if format == "cv2":
            return cv2.imread(path_file, 0)
        elif format == "dj":
            return File(open(path_file, "rb"))

    def create_or_update_intensity(self, intensity_data, collection_id, q_collection_id):
        """
        saves intensity
        :param intensity_data:
        :param collection_id:
        :param q_collection_id:
        :return:
        """
        q_path = os.path.join(self.collections_path, collection_id, q_collection_id)

        if not os.path.exists(q_path):
            os.makedirs(q_path)

        file_path = os.path.join(self.collections_path, collection_id, q_collection_id, "intensity.csv")
        intensity_data.to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')

    def read_intensity(self, collection_id, q_collection_id):
        file_path = os.path.join(self.collections_path, collection_id, q_collection_id, "intensity.csv")
        return pd.read_csv(file_path, sep='\t', index_col=0)

    def create_or_update_std(self, std_data, collection_id, q_collection_id):
        """
        saves std
        :param std_data:
        :param collection_id:
        :param q_collection_id:
        :return:
        """
        q_path = os.path.join(self.collections_path, collection_id, q_collection_id)

        if not os.path.exists(q_path):
            os.makedirs(q_path)

        file_path = os.path.join(self.collections_path, collection_id, q_collection_id, "std.csv")
        std_data.to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')

    def read_std(self, collection_id, q_collection_id):
        file_path = os.path.join(self.collections_path, collection_id, q_collection_id, "std.csv")
        return pd.read_csv(file_path, sep="\t", index_col=0)

    def write_rsc_to_master(self, collection_id, dic_data):
        collection_path = os.path.join(self.collections_path, collection_id)
        if not os.path.exists(collection_path):
            os.makedirs(collection_path)

        self.create_or_update_unique_gal_lig1(dic_data["gal_lig1"][1])
        self.create_or_update_unique_gal_lig2(dic_data["gal_lig2"][1])
        self.create_or_update_gal_lig1(dic_data["gal_lig1"][1], collection_id)
        self.create_or_update_gal_lig2(dic_data["gal_lig2"][1], collection_id)
        self.create_or_update_meta(dic_data["meta"], collection_id)
        #self.create_or_update_image(dic_data["image"][1], collection_id)
        self.write_steps(dic_data["process"], collection_id)
        self.create_or_update_images(dic_data["images"][1],collection_id)

    def write_sc_to_master(self,collection_id,q_collection_id,dic_data_sc):

        self.create_or_update_intensity(dic_data_sc["intensity"], collection_id, q_collection_id)
        self.create_or_update_std(dic_data_sc["std"], collection_id, q_collection_id)
        rel_path = os.path.join(collection_id, q_collection_id)
        self.create_or_update_meta(dic_data_sc["meta"], rel_path)

    def write_complete_rsc_to_master(self, data_dic_rsc):
        self.write_rsc_to_master(data_dic_rsc["meta"]["sid"],data_dic_rsc)
        for sc_id in data_dic_rsc["spot_collections"].keys():
            self.write_sc_to_master(data_dic_rsc["meta"]["sid"],sc_id,data_dic_rsc["spot_collections"][sc_id])

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
        dic_data["meta"] = self.read_meta(collection_id)
        dic_data["steps"] = self.read_steps(collection_id)
        dic_data["gal_ligand1"] = self.read_gal_ligand(collection_id, format="dj")
        dic_data["gal_ligand2"] = self.read_gal_virus(collection_id, format="dj")
        dic_data["images"] = self.read_images(collection_id)

        try:
            dic_data["intensity"] = self.read_intensity(collection_id, ".")
        except:
            pass
        return dic_data

    def read_study(self,study_id):
        pass

    def read_dic_spots(self, collection_id):
        dic_data = {}
        dic_data["gal_ligand1"] = self.read_gal_ligand(collection_id)[0]
        dic_data["gal_ligand2"] = self.read_gal_virus(collection_id)[0]
        dic_data["meta"] = self.read_meta(collection_id)
        return dic_data

    def read_q_collection(self, collection_id, q_collection_id):
        dic_data = {}
        dic_data["gal_ligand1"] = self.read_gal_ligand(collection_id)[0]
        dic_data["gal_ligand2"] = self.read_gal_virus(collection_id)[0]
        dic_data["meta"] = self.read_meta(collection_id)
        dic_data["intensity"] = self.read_intensity(collection_id, q_collection_id)
        try:
            dic_data["std"] = self.read_std(collection_id, q_collection_id)
        except:
            pass
        return dic_data

    def read_all_q_collection_ids_for_collection(self, collection_id):
        collection_path = os.path.join(self.collections_path, collection_id)
        q_collections = next(os.walk(collection_path))[1]
        return q_collections

    def create_or_update_unique_gal_lig1(self, gal_lig):
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
            result = re.search('lig_fix_(.*).txt', fn)
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
            # else: create  a new file
            created = True
            fname = 'lig_fix_' + '{:03}'.format(max_name + 1) + '.txt'
            fpath = os.path.join(self.unique_lig_gal_path, fname)
            gal_lig.to_csv(fpath, sep='\t')
        return fname, fpath, created

    def get_unique_gal_lig1(self, gal_lig):
        if not os.path.exists(self.unique_lig_gal_path):
            os.makedirs(self.unique_lig_gal_path)
        for fn in os.listdir(self.unique_lig_gal_path):
            file_path = os.path.join(self.unique_lig_gal_path, fn)
            # reads the matching file
            gal_ligand_master = pd.read_csv(file_path, sep='\t', index_col="ID")
            if gal_lig.equals(gal_ligand_master):
                fname = fn
                fpath = os.path.join(self.unique_lig_gal_path, fname)
                return fname, fpath
        return IOError("unique_gal_lig not found")

    def get_unique_gal_lig2(self, gal_vir):
        for fn in os.listdir(self.unique_vir_gal_path):
            file_path = os.path.join(self.unique_vir_gal_path, fn)
            # reads the matching file
            gal_virus_master = pd.read_csv(file_path, sep='\t', index_col="ID")
            if gal_vir.equals(gal_virus_master):
                fname = fn
                fpath = os.path.join(self.unique_lig_gal_path, fname)
                return fname, fpath
        return IOError("unique_gal_lig not found")

    def create_or_update_unique_gal_lig2(self, gal_vir):
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
            result = re.search('lig_mob_(.*).txt', fn)
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
            fname = 'lig_mob_' + '{:03}'.format(max_name + 1) + '.txt'
            fpath = os.path.join(self.unique_vir_gal_path, fname)
            gal_vir.to_csv(fpath, sep='\t')

        return fname, fpath, created

    def write_db_to_master(self):
        datatables_loaded = flutype.data_management.fill_database.DBDjango().load_database()
        self.write_data_tables(datatables_loaded)
        rscs = RawSpotCollection.objects.all()
        for rsc in rscs:
            data_dic_rsc = flutype.data_management.fill_database.DBDjango().load_complete_collection_from_db(rsc)
            self.write_complete_rsc_to_master(data_dic_rsc)


####################################################################
if __name__ == "__main__":
    ''' 
    WRITES EVERYTHING IN MASTER;
    !!! OVERWRITES EXISTING DATA !!!
    '''
    write_master = False

    # path to the master folder
    path_master = "master/"
    if write_master:
        ma = Master(path_master).write_db_to_master()

