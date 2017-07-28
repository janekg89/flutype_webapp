from __future__ import print_function, absolute_import, division

import os
import sys
import cv2
import csv
from flutype_analysis import utils, analysis

# setup django (add current path to sys.path)
path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))

if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flutype_webapp.settings")

import django

django.setup()
from flutype.data_management.read_flutype_analysis_db import load_procedure_data



# fixme: get or create to update_or_create()
class Master(object):

    def __init__(self, path):

        """
        :param path: The path to the Master Directory

        """
        self.path = path
        #self.collections = next(os.walk(path))[1]




    def create_or_update_gal_ligand(self,gal_ligand_data,collection_id):

        file_path = os.path.join(self.path, collection_id, "gal_ligand.csv")
        gal_ligand_data.to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')


    def create_or_update_gal_virus(self,gal_virus_data,collection_id):

        file_path = os.path.join(self.path, collection_id, "gal_virus.csv")
        gal_virus_data.to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')


    def create_or_update_meta(self,meta_data,collection_id):

        path_file = os.path.join(self.path, collection_id, 'meta.csv')
        with open(path_file, 'wb') as f:
            w = csv.DictWriter(f, meta_data.keys(), delimiter="\t")
            w.writeheader()
            w.writerow(meta_data)

    def create_or_update_image(self,image_data, collection_id):
        path_file = os.path.join(self.path,collection_id,"image.jpg")
        cv2.imwrite(path_file, image_data)

    def create_or_update_intensity(self, intensity_data, collection_id,q_collection_id):

        file_path = os.path.join(self.path,  collection_id,q_collection_id, "intensity.csv")
        intensity_data.to_csv(path_or_buf=file_path, sep="\t", encoding='utf-8')

    def create_or_update_std(self, std_data, collection_id,q_collection_id):

        file_path = os.path.join(self.path, collection_id,q_collection_id, "std.csv")
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
        collection_path = os.path.join(self.path,collection_id)
        q_collection_path = os.path.join(collection_path, q_collection_id)

        if not os.path.exists(collection_path):
            os.makedirs(collection_path)


        print("quantified_only", quantified_only)



        if q_collection_id == "not":
            self.create_or_update_gal_ligand(dic_data["gal_ligand"], collection_id)
            self.create_or_update_gal_virus(dic_data["gal_virus"], collection_id)
            self.create_or_update_meta(dic_data["meta"], collection_id)
            if type == "microarray":
                if "image" in dic_data:
                    self.create_or_update_image(dic_data["image"], collection_id)
            elif type =="microwell":
                self.create_or_update_intensity(dic_data["intensity"], collection_id=collection_id, q_collection_id=q_collection_id)

        elif quantified_only:

            if not os.path.exists(q_collection_path):
                os.makedirs(q_collection_path)

            self.create_or_update_intensity(dic_data["intensity"], collection_id=collection_id, q_collection_id=q_collection_id)
            if "std" in dic_data:
                self.create_or_update_std(dic_data["std"], collection_id=collection_id, q_collection_id=q_collection_id)

        else:
            if not os.path.exists(q_collection_path):
                os.makedirs(q_collection_path)


            self.create_or_update_gal_ligand(dic_data["gal_ligand"], collection_id)
            self.create_or_update_gal_virus(dic_data["gal_virus"], collection_id)
            self.create_or_update_meta(dic_data["meta"], collection_id)
            if "image" in dic_data:
                self.create_or_update_image(dic_data["image"], collection_id)
            if "intensity" in dic_data:
                self.create_or_update_intensity(dic_data["intensity"], collection_id=collection_id, q_collection_id=q_collection_id)
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



    def read_collection(self,collection, quantified=False):
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
        pass

    def create_or_update_all_raw_collection(self, dic_collections):
        """
        creates or updates all collections which are in the dic_collection as keys.
        :param dic_collections:  a dictionary:
                                    keys (values) -> sid_collection  (dictionary: dic_data) <- as described zb. in (create_or_update_collection)


        :return:
        """
        collections =[]
        #for collection in self.collections:
        #    collections.append(self.create_or_update_collection(collection, dic_collections[collection]))


if __name__ == "__main__":


    # fill master/collections
    path_master_collections = "../../media/master/"





    PATTERN_DIR_MICROARRAY = "../../../flutype_analysis/data/{}"
    PATTERN_DIR_MICROWELL = "../../../flutype_analysis/data/MTP/{}"

    microarray_collection_ids = [
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
    microwell_collection_ids = ["2017-05-12_MTP_R1",
                          "2017-06-13_MTP"
                          ]
    for collection_id in microarray_collection_ids:

        dic_data = utils.load_data(collection_id, PATTERN_DIR_MICROARRAY.format(collection_id))

        dic_data["gal_virus"] = dic_data.pop("gal_vir")
        dic_data["gal_ligand"] = dic_data.pop("gal_pep")
        dic_data["meta"] = load_procedure_data(PATTERN_DIR_MICROARRAY.format(collection_id))
        if "tif" in dic_data:
            dic_data["image"]= dic_data.pop("tif")
        if "data" in dic_data:
            dic_data["intensity"] = dic_data.pop("data")
        elif "data_std" in dic_data:
            dic_data["std"] = dic_data.pop("data_std")


        Master(path_master_collections).create_or_update_collection(collection_id, dic_data, q_collection_id="q001", quantified_only=False, type="microarray")
    """
        for collection_id in microwell_collection_ids:
        dic_data = utils.load_data(collection_id, PATTERN_DIR_MICROARRAY.format(collection_id))
        dic_data["intensity"] = dic_data.pop("data")
        dic_data["std"] = dic_data.pop("data_std")

        Master(path_master_collections).create_or_update_collection(collection_id, dic_data, q_collection_id="Q001",
                                                                    quantified_only=False, type="microwell")

    """










