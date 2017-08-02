from __future__ import print_function, absolute_import, division
import os
import sys
import cv2
import csv
import numpy as np
import pyexcel as pe
import pandas as pd


# setup django (add current path to sys.path)
path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))

if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flutype_webapp.settings")
import django
django.setup()

from flutype_analysis import utils

########################################################################################################################

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
    dic_microarray = {"SID": name_array[0,1],"HolderBatch":name_array[1,1],"SurfaceSubstance":name_array[2,1],
         "Manfacturer": name_array[3,1]}
    dic_microwell = {"SID": name_array[0,7],"HolderBatch":name_array[1,6],"SurfaceSubstance":name_array[2,7],
         "Manfacturer": name_array[3,7]}
    if any(dic_microarray.values()):
        print("Sample Holder is a microarray.")
        dic_microarray["HolderType"]= "microarray"
        dic_microarray.update(dic_all)
        return dic_microarray

    elif any(dic_microwell.values()):
        print("Sample Holder is a microwell plate.")
        dic_microwell["HolderType"] = "microwell"
        dic_microwell.update(dic_all)
        return dic_microwell



#load all peptide (batches), viruses (batches), procedures.
def load_db_from_formular(path):
    """

    :param path:
    :return: dictionary
    """
    d = {}
    d["peptide"] = load_peptide_data(path)
    d["peptide_batch"]= load_peptide_batch_data(path)
    d["virus"] = load_virus_data(path)
    d["virus_batch"] = load_virus_batch_data(path)
    d["spotting"]  = load_treatment_data("Spotting", path)
    d["quenching"] = load_treatment_data("Quenching", path)
    d["incubating"] = load_treatment_data("Incubating", path)
    return d
########################################################################################################################



















