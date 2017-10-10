from __future__ import print_function, absolute_import, division
import os
import sys

###############################################
# setup django (add current path to sys.path)
BASEPATH = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))

if BASEPATH not in sys.path:
    sys.path.append(BASEPATH)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flutype_webapp.settings")

import django
django.setup()

from flutype.helper import read_tsv_diconary , read_tsv_table

###############################################

STEPS = {"blocking","drying","incubating","incubatingAnalyt","quenching","scanning","spotting","washing"}
LIGANDS = {"antibody","peptide","virus"}
LIGAND_BATCHES =  {"antibodyBatch","peptideBatch","virusBatch","complexBatch","bufferBatch"}

class BaseAll(object):
    def __init__(self, path):
        self.path = path


class Master(BaseAll):
    """ Class for operations on master files. """
    def __init__(self, path):

        BaseAll.__init__(self,path)
        self.path_study = os.path.join(self.path, "studies")
        self.study_sids = set(next(os.walk(self.path_study))[1])
        self.path_process_steps = os.path.join(self.path, "process_steps")

        #all step types
        self.steps = STEPS

        #all ligand types
        self.ligands = LIGANDS
        self.ligand_batches =  LIGAND_BATCHES
        self.path_ligands = os.path.join(self.path, "ligands")




    def read_ligand_batches(self):
        dic_ligand_batches = {}

        for ligand_batch in self.ligand_batches:
            path_ligand_batch = os.path.join(self.path_ligands, "{}.tsv".format(ligand_batch))
            dic_ligand_batches[ligand_batch] =  read_tsv_table(path_ligand_batch)

        return dic_ligand_batches


    def read_ligands(self):
        dic_ligands = {}

        for ligand in self.ligands:
            path_ligand = os.path.join(self.path_ligands, "{}.tsv".format(ligand))
            dic_ligands[ligand] = read_tsv_table(path_ligand)

        return dic_ligands

    def read_complex(self):
        complex_dic = {}
        path_complex = os.path.join(self.path_ligands, "complex.tsv")
        complex_dic["complex"]= read_tsv_table(path_complex)
        return complex_dic

    def read_steps(self):

        dic_steps = {}
        for step in self.steps:
            path_step = os.path.join(self.path_process_steps,"{}.tsv".format(step))
            dic_steps[step]= read_tsv_table(path_step)
        return dic_steps

    def read_studies(self):
        dic_studies = {}
        for study in self.study_sids:
            study_path = os.path.join(self.path_study, study)
            dic_studies[study] = Study(study_path).read()
        return dic_studies



    def read(self):
        dic_master = {"studies":self.read_studies(),
                  "ligands":self.read_ligands(),
                  "ligand_batches":self.read_ligand_batches(),
                  "steps":self.read_steps()}
        return dic_master


class Base(BaseAll):
    def __init__(self,path):
        BaseAll.__init__(self,path)
        self.path_meta = os.path.join(self.path, "meta.tsv")
        self.meta = read_tsv_diconary(self.path_meta)
        self.sid = os.path.basename(os.path.abspath(self.path))
        self.path_raw_docs = os.path.join(self.path, "raw_docs")
        self.raw_docs_fnames = set(next(os.walk(self.path_raw_docs))[2])
        self.raw_docs_fpaths = set(self.get_raw_docs_fpaths())

    def get_raw_docs_fpaths(self):
        docs = []
        for doc in self.raw_docs_fnames:
            f_path = os.path.join(self.path_raw_docs, doc)
            docs.append(f_path)
        return docs

    def get_meta(self):
        self.meta["sid"]= self.sid
        return self.meta


class Study(Base):
    "Class for operations on a study"
    def __init__(self, path):
        Base.__init__(self,path)
        self.Master = Master(os.path.join(self.path, "../.."))
        self.path_measurements = os.path.join(self.path, "measurements")
        self.measurement_sids = set(next(os.walk(self.path_measurements))[1])




    def read(self):
        dic_study = {"meta":self.get_meta(),
                     "raw_docs_fpaths": self.raw_docs_fpaths,
                     "measurements":self.read_measurements(),
                     }
        return dic_study



    def read_measurements(self):
        dic_measurements = {}
        for measurement in self.measurement_sids:
            path_measurement = os.path.join(self.path_measurements,measurement)
            dic_measurements[measurement] = Measurement(path_measurement).read()

        return dic_measurements



    def write(self,dict):
        pass



class Measurement(Base):
    "Class for operations on a Measurement"
    def __init__(self, path):
        Base.__init__(self,path)
        self.Study = Study(os.path.join(self.path, "../.."))

        self.path_mob_lig = os.path.join(self.path, "lig_mob.txt")
        self.path_fix_lig = os.path.join(self.path, "lig_fix.txt")
        self.path_steps = os.path.join(self.path, "steps.tsv")

        self.path_results = os.path.join(self.path,"results")
        self.results_sids = set(next(os.walk(self.path_results))[1])


    def read(self):
        dic_measurement = {"meta":self.get_meta(),
                           "lig_mob_path":self.path_mob_lig,
                           "lig_fix_path":self.path_fix_lig,
                           "steps_path":self.path_steps,
                           "raw_docs_fpaths":self.get_raw_docs_fpaths(),
                           "results":self.read_results()
                           }
        return dic_measurement


    def read_results(self):
        dic_results = {}
        for result in self.results_sids:
            path_result = os.path.join(self.path_results,result)
            dic_results[result] = MeasurementResult(path_result).read()
        return dic_results


    def write(self, dict):
        pass


class MeasurementResult(Base):
    "Class for operations on "
    def __init__(self, path):
        Base.__init__(self,path)
        self.Measurement = Measurement(os.path.join(self.path, "../.."))

        self.path_intensity = os.path.join(self.path, self.meta["intensity_file"])
        self.intensity = read_tsv_table(self.path_intensity)



    def read(self):
        dic_results ={"meta":self.get_meta(),
                    "intensity":self.intensity,
                    }
        return dic_results

    def write(self, dic_results):
        pass

if __name__ == "__main__":

    MASTERPATH=os.path.join(BASEPATH,"Master_new")
    #Master(MASTERPATH).write()


        #todo how to you call it that you can write -- and - commands in the terminal with arguments (parse?)