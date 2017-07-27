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

if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flutype_webapp.settings")

import django

django.setup()


# fixme: get or create to update_or_create()
class Master(object):

    def __init__(self, path):

        """
        :param path: The path to the Master Directory

        """
        self.path = path
        self.collections = next(os.walk(path))[1]

    def create_or_update_collection(self, collection, dic_data, quantified=False, quantified_only=False):

        """
        The method is updating the desired data in the collection folder of one collection. The keys corresond to the specific data, which shell by updated.
        :param  collection: collection sid
        :param  dic_data: a dictionary containing one of the following keys. Their values contain the corresponding data:
                            keys (data_format):     gal_ligand   (pandas.DataFrame -> Columns: "Row", "Column", "Name")
                                                    gal_virus    (pandas.DataFrame -> Columns: "Row", "Column", "Name")
                                                    meta         (dictionary -> keys with corresponding value go to meta.csv)
                                                    image        (cv2 image file in grayscale)
                                                    data         (pandas.DataFrame -> Columns: "Columns" Index:"Row" Value: Intenstities)
                                                    std          (pandas.DataFrame -> Columns: "Columns" Index:"Row" Value: Standard deviation)
                                                    q_meta       (dictionary -> keys with corresponding value go to q_meta.csv)
        :param  quantified:                        False -> Only raw data is updated. The following keys are taken into cosiderations:
                                                          (for Microarrays: gal_ligand, gal_virus, meta, image)
                                                          (for Microwell plate: gal_ligand, gal_virus, meta, image)
                            "quantified_collection_name" ->  An extra folder with "quantified_collection_name" is generated with
                                                            (std, data, q_meta)

        :return:
        """

        pass


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
        for collection in self.collections:
            collections.append(self.create_or_update_collection(collection, dic_collections[collection]))

    










