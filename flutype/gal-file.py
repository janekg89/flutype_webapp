import pandas as pd
import os
# -*- coding: utf-8 -*-
from flutype.data_management.fill_master import Master

def print_full(x):
    pd.set_option('display.max_rows', len(x))
    print(x)
    pd.reset_option('display.max_rows')

def extract_peptide_batch(ma):
    gal_lig_fix = ma.read_gal_ligand("170725_N13", index=False)
    unique_peptides = gal_lig_fix[0].drop_duplicates(subset=["ID"])
    unique_peptides = unique_peptides[unique_peptides.ID != "Empty"]
    unique_peptides.ID = unique_peptides.ID.astype(int)
    unique_peptides.sort_values(by = "ID", inplace=True)
    unique_peptides.Name = unique_peptides.Name.str.replace('FAIL_', "")
    unique_peptides['Concentration'] = unique_peptides.Name.str.rpartition('_')[0]
    unique_peptides['Concentration'] = unique_peptides.Concentration.str.partition('_')[0]
    peptide_batch = pd.DataFrame(unique_peptides[["Name","Concentration"]].values,columns=["sid","concentration"])
    peptide_batch["labeling"] = ""
    peptide_batch["buffer"] = ""
    peptide_batch["ph"] = ""
    peptide_batch["purity"] = ""
    peptide_batch["produced_by"] = ""
    peptide_batch["comment"] = ""
    peptide_batch["ligand"] = ""
    peptide_batch["ligand"] = unique_peptides.Name.str.partition('_')[2].values
    return peptide_batch

def gal_reformat(ma):
    gal_lig_fix = ma.read_gal_ligand("170725_N13", index= False)
    gal_lig_fix_new = pd.DataFrame(gal_lig_fix[0][["Block","Row","Column","Name"]])
    mapping = {"Empty":"NO",
               "Panama":"Pan3",
               "California":"Cal2",
               "Aichi":"Ach1",
               "1.0_Kloe_Amid":"KLOA025",
               "0.5_Kloe_Amid":"KLOA050",
               "0.25_Kloe_Amid":"KLOA025",
               "1.0_pep_Nenad":"NEN100",
               "0.5_pep_Nenad":"NEN050",
               "0.25_pep_Nenad":"NEN025",
               "1.0_Fetuin":"P012-1",
               "0.5_Fetuin":"P012-05",
               "0.25_Fetuin":"P012-025",
               "1.0_Leuchtefix":"DYE100",
               "0.5_Leuchtefix":"DYE050",
               "0.25_Leuchtefix":"DYE025",
               'FAIL_': ""
               }
    for key in mapping:
        gal_lig_fix_new.Name = gal_lig_fix_new.Name.str.replace(key, mapping[key])

    mapping = {"1.0_Kloe_S":"KLOS100",
               "0.5_Kloe_S":"KLOS050",
               "0.25_Kloe_S":"KLOS025"
               }
    for key in mapping:
        gal_lig_fix_new.loc[gal_lig_fix_new["Name"].str.contains(key), "Name"] = mapping[key]
    return gal_lig_fix_new

def peptide_batches_not_in_master(ma,gal_lig_fix):
    s_gal = set(gal_lig_fix["Name"].values)
    data_dic = ma.read_data_tables()
    s_pb = set(data_dic["peptide_batch"]["sid"].values)
    s_ab = set(data_dic["antibody_batch"]["sid"].values)
    s_vb = set(data_dic["virus_batch"]["sid"].values)

    s_b = s_pb
    s_b.update(s_ab)
    s_b.update(s_vb)
    return(s_gal - s_b)

def reshape_gal_file(shape, gal_file):

    a = []
    b = []
    for i in range(shape[1]):
        for ii in range(shape[0]):
            a.append(i )
            b.append(ii )

    gal_file["row_factor"] = 0
    gal_file["column_factor"] = 0

    print(a)
    print(b)

    for block_num,block_factor  in enumerate(a):
        gal_file.loc[gal_file["Block"] == block_num+1, "row_factor"] = block_factor
    for block_num, block_factor in enumerate(b):
        gal_file.loc[gal_file["Block"] == block_num+1, "column_factor"] = block_factor

    gal_file["Row"]=gal_file["Row"]+(gal_file["Row"].max()*gal_file["row_factor"])
    gal_file["Column"]=gal_file["Column"]+(gal_file["Column"].max()*gal_file["column_factor"])

    return gal_file


####################################################################
if __name__ == "__main__":
    ma_path = "../master_uncomplete/"
    ma = Master(ma_path)
    #peptide_batch = extract_peptide_batch(ma)
    # print_full(peptide_batch)
    #fp = os.path.join(ma.collections_path,"170725_N13","peptides_batch.csv")
    # peptide_batch.to_csv(fp)
    ma_path_standard = "../master/"
    ma_standard = Master(ma_path_standard)
    gal_lig_fix = gal_reformat(ma)
    #subset = peptide_batches_not_in_master(ma_standard,gal_lig_fix)


    gal_lig_fix=  reshape_gal_file((4,8), gal_lig_fix)
    gal_lig_fix = gal_lig_fix.reset_index(drop=True)
    fp = os.path.join(ma.collections_path,"170725_N13","lig_fix_012.txt")
    gal_lig_fix.to_csv(fp, sep='\t',index=True , index_label="ID")
    gal_lig_fix["Name"] = "Pan3"
    fp2 = os.path.join(ma.collections_path,"170725_N13","lig_mob_012.txt")
    gal_lig_fix.to_csv(fp2, sep='\t', index=True,index_label="ID")

