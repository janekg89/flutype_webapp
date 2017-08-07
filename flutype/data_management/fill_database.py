"""
Script for filling database from backup
"""
from __future__ import print_function, absolute_import, division

import os
import sys
from django.core.files import File
import warnings

###########################################################
# setup django (add current path to sys.path)
path = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../'))
print(path)
if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flutype_webapp.settings")

import django
django.setup()

# the path to the master folder
path_master = os.path.join(path, "master/")

# all sid of microarray collections
# FIXME: get from folder names
collection_ids = ["2017-05-19_E5_X31",
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
                  "2017-05-19_N7_Cal",
                  "2017-05-12_MTP_R1",
                  "2017-06-13_MTP"
]


###########################################################
from django.contrib.auth.models import User
from flutype.data_management.fill_master import Master
from flutype.models import (Peptide,
                            PeptideBatch,
                            Virus,
                            VirusBatch,
                            Antibody,
                            AntibodyBatch,
                            Ligand,
                            RawSpotCollection,
                            SpotCollection,
                            RawSpot,
                            Spot,
                            Spotting,
                            Quenching,
                            Incubating,
                            Washing,
                            Drying,
                            ProcessStep,
                            Process,
                            GalFile,
                            Step,
                            Experiment
                            )

def get_user_or_none(dict):
    if "user" in dict:
        if dict["user"] is None:
            user = None
        else:
            user = User.objects.get(username=dict["user"])
    else:
        user = None

    return user
def get_step_or_none(dict):
    if "sid" in dict:
        if dict["sid"] is None:
            step = None
        else:
            step = Step.objects.get(sid=dict["sid"])
    else:
        step = None

    return step



class Database(object):
    """ Database """
    ##### helper functions  ########

    ##### create_or_update datables realted data ####
    def create_or_update_virus(self, virus):
        vir, created = Virus.objects.get_or_create(sid=virus["sid"],
                                                   comment=virus["comment"],
                                                   tax_id=virus["tax_id"],
                                                   link_db=virus["link_db"],
                                                   subtype=virus["subtype"],
                                                   isolation_country=virus["isolation_country"],
                                                   collection_date=virus["collection_date"],
                                                   strain=virus["strain"]
                                                   )
        return vir, created

    def create_or_update_virus_batch(self, virus_batch):
        if "lig_id" in virus_batch:
            print(virus_batch["lig_id"])
            if virus_batch["lig_id"] is None:
                virus = None
            else:
                virus = Virus.objects.get(sid=virus_batch["lig_id"])
        else:
            virus = None
            # prints all virus batches without foreignkey to a virus in the database
            print("No virus found for virus batch with sid:" + virus_batch["sid"])

        user = get_user_or_none(virus_batch)
        # fills virus batches
        virus_b, created = VirusBatch.objects.get_or_create(sid=virus_batch["sid"],

                                                            labeling=virus_batch["labeling"],
                                                            concentration=virus_batch["concentration"],
                                                            buffer=virus_batch["buffer"],
                                                            ph=virus_batch["ph"],
                                                            purity=virus_batch["purity"],
                                                            produced_by=user,
                                                            production_date=virus_batch["production_date"],
                                                            comment=virus_batch["comment"],
                                                            passage_history=virus_batch["passage_history"],
                                                            active=virus_batch["active"],
                                                            ligand=virus
                                                            )
        return virus_b, created


    def create_or_update_peptide(self, peptide):
        # fills peptides
        peptide, created = Peptide.objects.get_or_create(sid=peptide["sid"],
                                                         comment=peptide["comment"],
                                                         name=peptide["name"],
                                                         linker=peptide["linker"],
                                                         spacer=peptide["spacer"],
                                                         sequence=peptide["sequence"],
                                                         c_terminus=peptide["c-terminus"],
                                                         )
        return peptide, created



    def create_or_update_peptide_batch(self,peptide_batch):
        if "lig_sid" in peptide_batch:
            peptide = Peptide.objects.get(sid=peptide_batch["lig_sid"])

        else:
            peptide = None
            # prints all peptide batches without foreignkey to a peptide in the database
            print("No peptide found for peptide batch with sid:" + peptide_batch["sid"])

        user = get_user_or_none(peptide_batch)

        # fills peptide_batches
        peptide_b, created = PeptideBatch.objects.get_or_create(sid=peptide_batch["sid"],
                                                                ligand=peptide,
                                                                concentration=peptide_batch["concentration"],
                                                                ph=peptide_batch["ph"],
                                                                purity=peptide_batch["purity"],
                                                                buffer=peptide_batch["buffer"],
                                                                produced_by=user,
                                                                production_date=peptide_batch["production_date"],
                                                                comment=peptide_batch["comment"],
                                                                )
        return peptide_b, created


    def create_or_update_antibody(self,antibody):

        antibod, created = Antibody.objects.get_or_create(sid=antibody["sid"],
                                                         target=antibody["target"],
                                                         name=antibody["name"],
                                                         link_db=antibody["link_db"]
                                                         )
        return antibod, created

    def create_or_update_antibody_batch(self,antibody_batch):

        if "lig_sid" in antibody_batch:
            antibody = Antibody.objects.get(sid=antibody_batch["lig_sid"])

        else:
            antibody = None
            # prints all antibody batches without foreignkey to a antibody in the database
            print("No antibody found for antibody batch with sid:" + antibody_batch["sid"])

        user = get_user_or_none(antibody_batch)

        antibody_b, created =AntibodyBatch.objects.get_or_create(sid=antibody_batch["sid"],
                                                                 ligand=antibody,
                                                                 concentration=antibody_batch["concentration"],
                                                                 ph=antibody_batch["ph"],
                                                                 purity=antibody_batch["purity"],
                                                                 buffer=antibody_batch["buffer"],
                                                                 produced_by=user,
                                                                 production_date=antibody_batch["production_date"],
                                                                 comment=antibody_batch["comment"]
                                                                 )
        return  antibody_b, created

    def create_or_update_washing(self,washing):
        washing, created = Washing.objects.get_or_create(sid=washing["sid"],
                                                          method=washing["method"],
                                                          duration=washing["duration"],
                                                          substance=washing["substance"])
        return washing , created

    def create_or_update_quenching(self, quenching):
        quenching, created = Quenching.objects.get_or_create(sid=quenching["sid"],
                                                         method=quenching["method"],
                                                         duration=quenching["duration"],
                                                         substance=quenching["substance"])
        return quenching, created

    def create_or_update_drying(self, drying):
        drying, created = Drying.objects.get_or_create(sid=drying["sid"],
                                                         method=drying["method"],
                                                         duration=drying["duration"],
                                                         substance=drying["substance"])
        return drying, created


    def create_or_update_spotting(self, spotting):
        spotti, created = Spotting.objects.get_or_create(sid=spotting["sid"],
                                                         method=spotting["method"],
                                                        )
        return spotti, created



    def create_or_update_incubating(self, incubating):
        incub, created = Incubating.objects.get_or_create(sid=incubating["sid"],
                                                          method=incubating["method"],
                                                          duration=incubating["duration"]
                                                          )
        return incub, created








    def fill_dt(self,data_tables):
        # Stores informations if any new media was loaded.
        created_p = []
        created_pb = []
        created_v = []
        created_vb = []
        created_a = []
        created_ab = []

        #treatments
        created_s = []
        created_q = []
        created_i = []
        created_w = []
        created_d = []

        # fills ligands #############################
        for k, virus in data_tables["virus"].iterrows():
            _, created = self.create_or_update_virus(virus)
            created_v.append(created)

        for k, virus_batch in data_tables["virus_batch"].iterrows():
           _, created = self.create_or_update_virus_batch(virus_batch)
           created_vb.append(created)

        for k, peptide in data_tables["peptide"].iterrows():
            _, created = self.create_or_update_peptide(peptide)
            created_p.append(created)

        for k, peptide_batch in data_tables["peptide_batch"].iterrows():
            _,created = self.create_or_update_peptide_batch(peptide_batch)
            created_pb.append(created)

        for k, antibody in data_tables["antibody"].iterrows():
            _,created = self.create_or_update_antibody(antibody)
            created_a.append(created)

        for k, antibody_batch in data_tables["antibody_batch"].iterrows():
            _,created = self.create_or_update_antibody_batch(antibody_batch)
            created_ab.append(created)

        ############################################
        for k, washing in data_tables["washing"].iterrows():
            print(washing)
            _, created = self.create_or_update_washing(washing)
            created_w.append(created)
        for k, drying in data_tables["drying"].iterrows():
            _, created = self.create_or_update_drying(drying)
            created_d.append(created)
        for k, spotting in data_tables["spotting"].iterrows():
            _, created = self.create_or_update_spotting(spotting)
            created_s.append(created)
        for k, quenching in data_tables["quenching"].iterrows():
            _, created = self.create_or_update_quenching(quenching)
            created_q.append(created)
        for k, incubating in data_tables["incubating"].iterrows():
            _, created = self.create_or_update_incubating(incubating)
            created_i.append(created)

        print("updates to database:")
        print("virus:", any(created_v))
        print("virus_batch:", any(created_vb))
        print("peptide:", any(created_p))
        print("peptide_batch:", any(created_pb))
        print("spotting:", any(created_s))
        print("quenching:", any(created_q))
        print("incubating:", any(created_i))
        print("washing:", any(created_w))
        print("drying:", any(created_d))

    def create_or_update_process(self,steps):
        steps_in_process = []

        for index, step in steps.iterrows():
            process_step = Step.objects.get(sid=dict["sid"])
            steps_in_process.append(process_step)

        max_id = 0
        for process in Process.objects.all():
            if process.sid > max_id:
                max_id = process.sid
            steps = list(process.steps.all())
            if steps == steps_in_process:
                return process , False

        process, created = Process.objects.get_or_create(sid=max_id)

        return process, created



    def create_or_update_process_and_process_steps(self, meta):
        """
        :param meta: (dictionary -> keys with corresponding value ->  meta.csv)
                    keys :Manfacturer
                          HolderType
                          HolderBatch
                          SID
                          SurfaceSubstance
                          Steps



        :return: process (Django.model object), created (True if created, False if found)
        """


        process, _ =self.create_or_update_process(meta["steps"])



        #experiment = Experiment.objects.get(sid=meta["sid"])
        for index,step in  meta["steps"].iterrows():
            process_step = get_step_or_none(step["sid"])
            user = get_user_or_none(step["user"])
            process_step, created = ProcessStep.objects.get_or_create(process = process,
                                                                      step=process_step,
                                                                      index=index,
                                                                      user=user,
                                                                      date=step["date"]
                                                                      )
        return process_step, created







    def fill_raw_collection(self,dic_data):
        """
         :param  dic_data: a dictionary containing one of the following keys. Their values contain the corresponding data:
                            keys (data_format):     gal_ligand    tuple (Django File, fname)
                                                    gal_virus     tuple (Django File, fname)
                                                    meta          (dictionary -> keys with corresponding value go to meta.csv)
                                                    image         Django File



        :return:
        """
        print("-" * 80)
        print("Filling Collection with sid <{}>".format(dic_data["meta"]["sid"]))


        process, process_created = self.create_or_update_process_and_process_steps(dic_data["meta"])

        gal_vir, gal_vir_created = self.fill_gal_vir(dic_data["gal_virus"][0],dic_data["gal_virus"][1])
        gal_lig, gal_lig_created = self.fill_gal_lig(dic_data["gal_ligand"][0],dic_data["gal_ligand"][1])


        # gets or creates raw_spot_collection
        raw_spot_collection, _ = RawSpotCollection.objects.get_or_create(sid=dic_data["meta"]["sid"],
                                                                             batch=dic_data["meta"]["holder_batch"],
                                                                             holder_type=dic_data["meta"]["holder_type"],
                                                                             functionalization=dic_data["meta"]['surface_substance'],
                                                                             manufacturer=dic_data["meta"]['manfacturer'],
                                                                             gal_ligand=gal_lig,
                                                                             gal_virus=gal_vir,
                                                                             process=process)
        if "image" in dic_data:
            raw_spot_collection.image.save(dic_data["meta"]["sid"]+".jpg", dic_data["image"])


    def fill_spot_collection(self, collection_id, q_collection_id):
        """
                                                            intensity     (pandas.DataFrame -> Columns: "Columns" Index:"Row" Value: Intenstities)

        :param collection:
        :param q_collection:
        :return:
        """
        raw_spot_collection = RawSpotCollection.objects.get(sid=collection_id)
        spot_collection, created = SpotCollection.objects.get_or_create(sid=q_collection_id,
                                                                        raw_spot_collection=raw_spot_collection
                                                                        )

        return spot_collection ,created, raw_spot_collection

    def fill_raw_spot(self, collection_id, raw_spot):

        raw_spot_collection = RawSpotCollection.objects.get(sid=collection_id)


        raw_spot, created = RawSpot.objects.get_or_create(peptide_batch=PeptideBatch.objects.get(sid=raw_spot["ligand"]),
                                                          virus_batch=VirusBatch.objects.get(sid=raw_spot["virus"]),
                                                          raw_spot_collection=raw_spot_collection,
                                                          column=raw_spot["column"],
                                                          row=raw_spot["row"]
                                                          )
        return raw_spot, created

    def fill_spot(self, raw_spot,spot_collection, spot):
        spo, created = Spot.objects.get_or_create(raw_spot=raw_spot,
                                          intensity=spot["intensity"],
                                          std=spot["std"],
                                          spot_collection=spot_collection)
        return spo, created



    def fill_gal_lig(self,gal_lig, fname_gal_lig):
        """

        :param  fname_gal_lig: name of _gal_ligand
        :param  gal_lig: gal ligand (django File format !)
        :return: gal_ligand, created
        """

        try:
            gal_ligand = GalFile.objects.get(sid=fname_gal_lig)
            created = False
        except:
            gal_ligand, created = GalFile.objects.get_or_create(sid=fname_gal_lig)
            gal_ligand.file.save(fname_gal_lig, File(gal_lig))

        return gal_ligand, created


    def fill_gal_vir(self, gal_vir, fname_gal_vir):
        """

        :param fname_gal_vir: name of gal_vir
        :param gal_vir : (django File format !)
        :return: gal_virus, created

        """

        try:
            gal_virus = GalFile.objects.get(sid=fname_gal_vir)
            created = False
        except:
            gal_virus, created = GalFile.objects.get_or_create(sid=fname_gal_vir)
            gal_virus.file.save(fname_gal_vir, File(gal_vir))

        return gal_virus, created


    def get_peptide_set(self,RawSpotCollection):
        """
        :return: a set of peptides which were used in RawSpotCollection
        """
        raw_spots = RawSpotCollection.rawspot_set.all()
        unique_peptide_sid = []

        for raw_spot in raw_spots:
            if raw_spot.peptide_batch.peptide.sid in unique_peptide_sid:
                pass
            else:
                unique_peptide_sid.append(raw_spot.peptide_batch.peptide.sid)
        return unique_peptide_sid

    def get_virus_set(self,RawSpotCollection):
        """
        :return: a set of viruses which were used in RawSpotCollection
        """
        raw_spots = RawSpotCollection.rawspot_set.all()
        unique_virus_sid = []

        for raw_spot in raw_spots:
            virus = raw_spot.virus_batch.virus
            if not hasattr(virus, 'sid'):
                warnings.warn(
                    "No connection between virus and virus batch for virus_batch: {}".format(raw_spot.virus_batch.sid))
            else:
                if virus.sid in unique_virus_sid:
                    pass
                else:
                    unique_virus_sid.append(raw_spot.virus_batch.virus.sid)
        return unique_virus_sid

    def get_spots_of_collection(self, dic_data):
        """ """
        vir_cor = dic_data["gal_ligand2"].pivot(index="Row", columns="Column", values="Name")
        pep_cor = dic_data["gal_ligand1"].pivot(index="Row", columns="Column", values="Name")

        # merge raw  spot information.
        vir_cor_unstacked = vir_cor.unstack()
        spot = pep_cor.unstack()
        spot = spot.reset_index()
        spot = spot.rename(columns={0: "Ligand"})
        spot["Virus"] = vir_cor_unstacked.values
        if "intensity" in dic_data:
            spot["Intensity"]= dic_data["intensity"].unstack().values

        if "std" in dic_data:
            spot["Std"] = dic_data["std"].unstack().values
        else:
            spot["Std"] = None

        return spot


    def fillmany2many_rawspots_peptides_viruses(self):
        """ """
        for rsc in RawSpotCollection.objects.all():
            virus_ids = self.get_virus_set(rsc)
            peptide_ids = self.get_peptide_set(rsc)

            for virus_id in virus_ids:
                try:
                    rsc.viruses.add(Virus.objects.get(sid=virus_id))
                except:
                    pass
            for peptide_id in peptide_ids:
                try:
                    rsc.peptides.add(Peptide.objects.get(sid=peptide_id))
                except:
                    pass


    def fill_raw_collection_and_related_raw_spots(self, dic_data, dic_spots):
        """ """
        self.fill_raw_collection(dic_data)
        # fill raw spots
        raw_spots = self.get_spots_of_collection(dic_spots)
        for k, raw_spot in raw_spots.iterrows():
            self.fill_raw_spot(dic_data["meta"]["sid"], raw_spot)



    def fill_q_collection_and_related_spots(self, dic_data_q, q_collection_id):
        """ """
        spot_collection, created, raw_spot_collection = self.fill_spot_collection(dic_data_q["meta"]["sid"],
                                                                                q_collection_id)
        spots = self.get_spots_of_collection(dic_data_q)
        for k, spot in spots.iterrows():
            raw_spo = RawSpot.objects.get(raw_spot_collection=raw_spot_collection,
                                          column=spot["Column"],
                                          row=spot["Row"]
                                          )
            self.fill_spot(raw_spot=raw_spo, spot_collection=spot_collection, spot=spot)


def fill_database(path_master, collection_ids):
    """ Main function to fill database

    :param path_master:
    :param collection_ids:
    :return:
    """
    print("-" * 80)
    print("Filling database")
    print("-" * 80)

    # loads data_tables
    ma = Master(path_master)

    db = Database()
    data_tables = ma.read_data_tables()
    db.fill_dt(data_tables)

    exit()

    # loads collection
    for collection_id in collection_ids:
        #fill raw collection
        dic_data_dj = ma.read_raw_collection(collection_id)
        dic_spots = ma.read_dic_spots(collection_id)
        db.fill_raw_collection_and_related_raw_spots(dic_data_dj, dic_spots)
        #fill_q_collection
        q_collection_ids = ma.read_all_q_collection_ids_for_collection(collection_id)
        for q_collection_id in q_collection_ids:
            dic_data_q = ma.read_q_collection(collection_id,q_collection_id)
            db.fill_q_collection_and_related_spots(dic_data_q, q_collection_id)

    #many 2many relation
    db.fillmany2many_rawspots_peptides_viruses()


##############################################################
if __name__ == "__main__":

    fill_database(path_master=path_master, collection_ids=collection_ids)

