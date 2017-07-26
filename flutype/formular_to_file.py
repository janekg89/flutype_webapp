from __future__ import print_function, absolute_import, division
import os
import sys
import cv2
import csv

# setup django (add current path to sys.path)
path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))

if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flutype_webapp.settings")
import django
django.setup()

from dbcreator import DBCreator as dbc
from flutype_analysis import utils




#load all peptide (batches), viruses (batches), procedures.
def load_db_from_formular(path):
    """

    :param path:
    :return: dictionary
    """
    d = {}
    d["peptide"] = dbc.load_peptide_data(path)
    d["peptide_batch"]= dbc.load_peptide_batch_data(path)
    d["virus"] = dbc.load_virus_data(path)
    d["virus_batch"] = dbc.load_virus_batch_data(path)
    d["spotting"]  = dbc.load_treatment_data("Spotting", path)
    d["quenching"] = dbc.load_treatment_data("Quenching", path)
    d["incubating"] = dbc.load_treatment_data("Incubating", path)
    return d

def write_dic_to_file(dic, path):
    for key in dic:
        file_name=  key + ".csv"
        file_path = os.path.join(path, file_name)
        dic[key].to_csv(path_or_buf=file_path , sep="\t", encoding='utf-8')
def write_img_to_file(img, path):
    name = "image.jpg"
    path_file = os.path.join(path, name)
    cv2.imwrite(path_file, img)

def write_meta_to_file(meta,path):
    name = 'meta.csv'
    path_file = os.path.join(path, name)
    with open(path_file, 'wb') as f:
        w = csv.DictWriter(f, meta.keys(),delimiter="\t")
        w.writeheader()
        w.writerow(meta)


def load_collection_data(from_path,to_path, data_id):

    #loads data from files fixme: add processed image.
    data = utils.load_data(data_id, from_path)
    del data['data_id']
    individual_path = os.path.join(to_path,data_id)

    if not os.path.exists(individual_path):
        os.makedirs(individual_path)
    if 'tif' in data:
        write_img_to_file(data["tif"], individual_path)
        del data["tif"]


    write_dic_to_file(data, individual_path)

    #loads data from form/process
    meta_dic = dbc.load_procedure_data(from_path)
    #writes to backup/collections
    write_meta_to_file(meta_dic, individual_path)





if __name__ == "__main__":
        #fill data_backup/data
        path_formular_db = "../media/forumular_db/"
        path_backup_data = "../media/data_backup/data/"
        d = load_db_from_formular(path_formular_db)
        write_dic_to_file(d,  path_backup_data)

        #fill data_backup/collections
        path_backup_collections = "../media/data_backup/collections"

        PATTERN_DIR_MICROARRAY = "../../flutype_analysis/data/{}"
        PATTERN_DIR_MICROWELL = "../../flutype_analysis/data/MTP/{}"

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
        for data_id in microarray_data_ids:
            load_collection_data(PATTERN_DIR_MICROARRAY.format(data_id),path_backup_collections,data_id)

        microwell_data_ids = ["2017-05-12_MTP_R1",
                              "2017-06-13_MTP"
                              ]
        for data_id in microwell_data_ids:
            load_collection_data(PATTERN_DIR_MICROWELL.format(data_id),path_backup_collections,data_id)













