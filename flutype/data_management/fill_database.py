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
                            Process,
                            GalFile
                            )


class Database(object):
    """ Database """

    def create_or_update_virus(self, virus):
        vir, created = Virus.objects.get_or_create(sid=virus["Taxonomy ID"],
                                                   tax_id=virus["Taxonomy ID"],
                                                   link_db=virus["Link_db"],
                                                   subtype=virus["SubGroup"],
                                                   isolation_country=virus["Country"],
                                                   collection_date=virus["Date"],
                                                   strain=virus["Strain Name"],

                                                 )
        return vir, created

    def create_or_update_virus_batch(self, virus_batch):
        if "Taxonomy ID" in virus_batch:
            ligand = Ligand.objects.get(sid=virus_batch["Taxonomy ID"])
        else:
            virus = None
            # prints all virus batches without foreignkey to a virus in the database
            print("No virus found for virus batch with sid:" + virus_batch["Batch ID"])

        if "user" in virus_batch:
            user = User.objects.get(username=virus_batch["user"])
        else:
            user = None
        # fills virus batches
        virus_b, created = VirusBatch.objects.get_or_create(sid=virus_batch["Batch ID"],
                                                            labeling=virus_batch["Labeling"],
                                                            concentration=virus_batch["Concentration [mg/ml]"],
                                                            buffer=virus_batch["Buffer"],
                                                            ph=virus_batch["pH"],
                                                            purity=virus_batch["purity"],
                                                            produced_by=user,
                                                            production_date=virus_batch["Production Date"],
                                                            comment=virus_batch["Comment"],

                                                            passage_history=virus_batch["Passage History"],
                                                            active=virus_batch["Active"],
                                                            virus=virus,

                                                            )
        return virus_b, created


    def create_or_update_peptide(self, peptide):
        # fills peptides
        peptide, created = Peptide.objects.get_or_create(sid=peptide["Peptide ID"],
                                                         name=peptide["Name"],
                                                         linker=peptide["Linker"],
                                                         spacer=peptide["Spacer"],
                                                         sequence=peptide["Sequence"],
                                                         c_terminus=peptide["C-terminus"],
                                                         pep_type=peptide["Types"],
                                                         comment=peptide["Comment"]
                                                         )
        return peptide, created



    def create_or_update_peptide_batch(self,peptide_batch):
        try:
            peptide = Peptide.objects.get(sid=peptide_batch["Peptide ID"])

        except:
            peptide = None
            # prints all peptide batches without foreignkey to a virus in the database
            print("No peptide found for peptide batch with sid:" +peptide_batch["Ligand id"])

        # fills peptide_batches
        peptide_b, created = PeptideBatch.objects.get_or_create(sid=peptide_batch["Ligand id"],
                                                        peptide=peptide,
                                                        concentration=peptide_batch["Concentration [mg/ml]"],
                                                        ph=peptide_batch["pH"],
                                                        purity=peptide_batch["Purity (MS)"],
                                                        buffer=peptide_batch["Buffer"],
                                                        produced_by=peptide_batch["Synthesized by"],
                                                        production_date=peptide_batch["Synthesization Date"],
                                                        comment=peptide_batch["Comment"]
                                                        )
        return peptide_b, created


    def create_or_update_anti_body(self,antibody):
        antibod,created = Antibody.objects.get_or_create(sid=antibody["Ligand id"],
                                                         )




    def create_or_update_incubating(self, incubating):
        incub, created = Incubating.objects.get_or_create(sid=incubating["Incubating ID"],
                                                         method=incubating["Incubation Method"],
                                                         date_time=None,
                                                         user=None,
                                                         comment=incubating["Comment"])
        return incub, created



    def create_or_update_quenching(self,quenching):
        quench, created = Quenching.objects.get_or_create(sid=quenching["Queching ID"],
                                                        method=quenching["Quenching Method"],
                                                        date_time=None,
                                                        user=None,
                                                        comment=quenching["Comment"])
        return quench , created

    def create_or_update_spotting(self, spotting):
        spotti, created = Spotting.objects.get_or_create(sid=spotting["Spotting ID"],
                                                    method=spotting["Spotting Method"],
                                                    date_time=None,
                                                    user=None,
                                                    comment=spotting["Comment"])
        return spotti, created


    def fill_dt(self,data_tables):
        # Stores informations if any new media was loaded.

        created_pb = []
        created_p = []
        created_v = []
        created_vb = []
        #treatments
        created_s = []
        created_q = []
        created_i = []

        # fills viruses
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

        for k, peptide_batch in data_tables["peptide_batch"].iterrows():
            _,created = self.create_or_update_peptide_batch(peptide_batch)
            created_pb.append(created)

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

    def fill_process(self, meta):
        """
        :param meta: (dictionary -> keys with corresponding value ->  meta.csv)
                    keys :Manfacturer
                          HolderType
                          Spotting
                          HolderBatch
                          Incubating
                          SID
                          SurfaceSubstance
                          Quenching


        :return: process (Django.model object), created (True if created, False if found)
        """
        try:
            spotting = Spotting.objects.get(sid=meta["Spotting"])
        except:
            spotting = None
        try:
            incubating = Incubating.objects.get(sid=meta["Incubating"])
        except:
            incubating = None
        try:
            quenching = Quenching.objects.get(sid=meta["Quenching"])
        except:
            quenching = None
        try:
            user = User.objects.get(username=meta["ProcessUser"])
        except:
            user = None


        process, created = Process.objects.get_or_create(spotting=spotting,
                                                         incubating=incubating,
                                                         quenching=quenching,
                                                         user=user)

        return process, created



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
        print("Filling Collection with sid <{}>".format(dic_data["meta"]["SID"]))

        process, priocess_created = self.fill_process(dic_data["meta"])
        gal_vir, gal_vir_created = self.fill_gal_vir(dic_data["gal_virus"][0],dic_data["gal_virus"][1])
        gal_lig, gal_lig_created = self.fill_gal_lig(dic_data["gal_ligand"][0],dic_data["gal_ligand"][1])


        # gets or creates raw_spot_collection
        raw_spot_collection, _ = RawSpotCollection.objects.get_or_create(sid=dic_data["meta"]["SID"],
                                                                             batch=dic_data["meta"]["HolderBatch"],
                                                                             holder_type=dic_data["meta"]["HolderType"],
                                                                             functionalization=dic_data["meta"]['SurfaceSubstance'],
                                                                             manufacturer=dic_data["meta"]['Manfacturer'],
                                                                             gal_ligand=gal_lig,
                                                                             gal_virus=gal_vir,
                                                                             process=process)
        if "image" in dic_data:
            raw_spot_collection.image.save(dic_data["meta"]["SID"]+".jpg", dic_data["image"])


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


        raw_spot, created = RawSpot.objects.get_or_create(peptide_batch=PeptideBatch.objects.get(sid=raw_spot["Ligand"]),
                                                          virus_batch=VirusBatch.objects.get(sid=raw_spot["Virus"]),
                                                          raw_spot_collection=raw_spot_collection,
                                                          column=raw_spot["Column"],
                                                          row=raw_spot["Row"]
                                                          )
        return raw_spot, created

    def fill_spot(self, raw_spot,spot_collection, spot):
        spo, created = Spot.objects.get_or_create(raw_spot=raw_spot,
                                          intensity=spot["Intensity"],
                                          std=spot["Std"],
                                          spot_collection=spot_collection)
        return spo, created



    def fill_gal_lig(self,gal_lig, fname_gal_lig):
        """

        :param  fname_gal_lig: name of _gal_ligand
        :param  gal_lig: gal ligand (django File format !)
        :return: gal_ligand, created
        """

        try:
            gal_ligand = GalLigand.objects.get(sid=fname_gal_lig)
            created = False
        except:
            gal_ligand, created = GalLigand.objects.get_or_create(sid=fname_gal_lig)
            gal_ligand.file.save(fname_gal_lig, File(gal_lig))

        return gal_ligand, created


    def fill_gal_vir(self, gal_vir, fname_gal_vir):
        """

        :param fname_gal_vir: name of gal_vir
        :param gal_vir : (django File format !)
        :return: gal_virus, created

        """

        try:
            gal_virus = GalVirus.objects.get(sid=fname_gal_vir)
            created = False
        except:
            gal_virus, created = GalVirus.objects.get_or_create(sid=fname_gal_vir)
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
        vir_cor = dic_data["gal_virus"].pivot(index="Row", columns="Column", values="Name")
        pep_cor = dic_data["gal_ligand"].pivot(index="Row", columns="Column", values="Name")

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
            self.fill_raw_spot(dic_data["meta"]["SID"], raw_spot)



    def fill_q_collection_and_related_spots(self, dic_data_q, q_collection_id):
        """ """
        spot_collection, created, raw_spot_collection = self.fill_spot_collection(dic_data_q["meta"]["SID"],
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

