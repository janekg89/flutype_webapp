"""
Script for creating and filling database.
"""
from __future__ import print_function, absolute_import, division

import os
from flutype_analysis import utils
import sys



# setup django
path = '/home/jan/Dev/Projects/flutype_webapp/'
if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flutype_webapp.settings")

import django
import numpy as np
import pandas as pd
import pyexcel as pe
django.setup()

from flutype.models import (Peptide, Peptide_batch, Virus, Virus_batch)  #import models


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
        return peptide_data

    @staticmethod
    def fill_db(data_id,directory):
        """ Reads the data and fills database.

        :param: fdata: directory containing data
        
        :return:
        """

        print("-"*80)
        print("Filling database")
        print("-" * 80)
        peptide_data = DBCreator.load_peptide_data(directory)
        Peptide.objects.get_or_create(name=peptide_data["Name"],
                                      linker=peptide_data["Linker"],
                                      spacer=peptide_data["Spacer"],
                                      sequence=peptide_data["Sequence"],
                                      c_terminus=peptide_data["C-terminus"]
                                      )



        data = utils.load_data(data_id,directory)




if __name__ == "__main__":

    # data
    #todo: loop through all data. But not for peptide db (the correct one is in "2017-05-19_E5_X31")
    data_id = "2017-05-19_E5_X31"
    directory = "../../flutype_analysis/data/{}/".format(data_id)


    pep_data = DBCreator().fill_db(data_id,directory)



