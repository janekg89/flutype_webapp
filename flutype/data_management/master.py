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



#fixme: get or create to update_or_create()
class Master(object):
    def __init__(self,path):
        """
        :param path: The path to the Master Directory

        """



    def update(self,dic_data):
        """
        :param dic_data: dictionary containing one of the following keys. There values are the corresponding data:
                        keys (data_format): gal_ligand   (pandas.DataFrame -> Columns: "Row", "Column", "Name")
                                            gal_virus    (pandas.DataFrame -> Columns: "Row", "Column", "Name")
                                            meta         (dictionary -> keys with corresponding value go to meta.csv)
                                            image        (dictoinary -> cv2 image file in grayscale)
                                            image_processed
                                            intensity
                                            std

        :return:
        """

        pass


