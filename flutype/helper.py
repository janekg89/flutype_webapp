
from __future__ import absolute_import, print_function, unicode_literals
from django.core.files.storage import FileSystemStorage
from flutype_webapp.settings import MEDIA_ROOT
from django.contrib.auth.models import User
from django_pandas.io import read_frame
from django.db import transaction
import os
import hashlib
from django.apps import apps
import datetime
import re
import tempfile
import sys
import io
import ast
import numpy as np
import pandas as pd





BASE_DIR = os.path.dirname(os.path.dirname(__file__))

CHAR_MAX_LENGTH = 100
def auto_get_or_create_ligand_batches(browser_input):
    data_ligandbatches = pd.DataFrame(browser_input, columns=range(1, 17), index=range(1, 13))
    concentration_unit = data_ligandbatches.loc[10, 14]
    ligandbatches = rows_and_cols_to_gal_file(data_ligandbatches.loc[:8, :12])

    ligandbatches["Name"].replace('', np.nan, inplace=True)
    ligandbatches.dropna(subset=['Name'], inplace=True)

    if ligandbatches.empty:
        ligandbatches["sid"] = ""

        return ligandbatches

    ligand_concentration_y = data_ligandbatches.loc[:8, 14]
    ligand_concentration_y = ligand_concentration_y.replace([None,""], "1")

    ligand_concentration_x = data_ligandbatches.loc[10, :12]
    ligand_concentration_x = ligand_concentration_x.replace([None,""], "1")

    c = outer_product(ligand_concentration_x, ligand_concentration_y)
    ligand_concentration = rows_and_cols_to_gal_file(pd.DataFrame(c, columns=range(1, 13), index=range(1, 9)))
    ligand_concentration.rename(columns={"Name": "concentration"}, inplace=True)

    ligandbatches.rename(columns={"Name": "ligandbatch"}, inplace=True)
    ligand_batches = pd.merge(ligandbatches, ligand_concentration, how='left', on=['Row', 'Column'])


    ligand_batches["sid"] = "*" + ligand_batches["ligandbatch"] + "-" + ligand_batches["concentration"] + "*"
    LigandBatch = apps.get_model("flutype", model_name="LigandBatch")
    for ligandbatch in ligand_batches["ligandbatch"].values:
        LigandBatch.objects.get_subclass(sid=ligandbatch)
    ligand_batches_stock = [LigandBatch.objects.get_subclass(sid=ligandbatch) for ligandbatch in ligand_batches["ligandbatch"].values]
    ligand_batches["ligandbatch_stock"] = ligand_batches_stock
    for index, ligandbatch in ligand_batches.iterrows():
        try:
            LigandBatch.objects.get_subclass(sid=ligandbatch["sid"])
        except:
            ligandbatch["ligandbatch_stock"].pk = None
            ligandbatch["ligandbatch_stock"].id = None
            ligandbatch["ligandbatch_stock"].ligandbatch_ptr_id = None
            ligandbatch["ligandbatch_stock"].sid =  ligandbatch["sid"]
            ligandbatch["ligandbatch_stock"].concentration = ligandbatch["concentration"]
            ligandbatch["ligandbatch_stock"].stock = False
            ligandbatch["ligandbatch_stock"].concentration_unit = concentration_unit
            ligandbatch["ligandbatch_stock"].save()

    return ligand_batches

def outer_product(df1, df2):
    x = list(map(float,df1.values))
    y = list(map(float,df2.values))
    return np.outer(y,x)

def camel_case_split(identifier):
    matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return " ".join([m.group(0) for m in matches])


def empty_list(max):
    list = []
    for n in range(max):
        list.append('')
    return list

def generate_tree(path):
    path_templates = os.path.join(BASE_DIR, "flutype/templates/flutype/")
    path_file = os.path.join(path_templates, "tree.html")
    #################
    os.system("tree {} -oH {} . --nolinks".format(path,path_file))
    return os.path.isfile(path_file)

def tar_tree(path):
    directory_dir = os.path.join(path,"170929-tutorial/")
    directory_to = os.path.join(path,"170929-tutorial/raw_docs/")
    path_file = os.path.join(directory_to,"tree.tar.gz")

    os.system("tar -czf {} {}".format(path_file,directory_dir))
    return os.path.isfile(path_file)


def unique_ordering(steps):
    if steps["step"].empty:
        vals = "NoSteps"
    else:
        order_steps = steps["step"]
        vals = '-'.join(order_steps)
    return vals

def md5(f):
    hash_md5 = hashlib.md5()
    for chunk in iter(lambda: f.read(4096), b""):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()

class OverwriteStorage(FileSystemStorage):
    """
    Overwrite storage overwrites existing names by deleting the resources.
    ! Use with care. This deletes files from the media folder !
    """

    def get_available_name(self, name, **kwargs):
        if self.exists(name):
            os.remove(os.path.join(MEDIA_ROOT, name))
        return name

def read_tsv_diconary(fpath):
    d={}
    with open(fpath, 'r') as f:
        for line in f:
            line =line.split("\t")
            if len(line) == 1:
                line.append("")
            key = line[0].strip()
            value = line[1].strip()
            if value == "TRUE":
                value = True
            if value == "":
                value = None
            if value =="FALSE":
                value = False
            d[key] = value

    return d


def read_tsv_table(fpath):
    table = pd.read_csv(fpath, sep="\t", encoding='utf-8', dtype=str)
    return table

def clean_step_table(table):
    table.dropna(axis=0, subset=['step'], how='all', inplace=True)
    return table

def read_and_dropnan(fpath):
    table = read_tsv_table(fpath)
    return nan_to_none_in_pdtable(table)

def nan_to_none_in_pdtable(table):
    table.replace([np.NaN], [None], inplace=True)
    return table


def write_tsv_table(df,fpath):
    df.replace([None], [np.NaN], inplace=True)
    df.to_csv(fpath,sep=str("\t"), encoding='utf-8', index=False)

def read_ligands(ligand):
    model = get_model_by_name(ligand)
    df = read_frame(model.objects.all())
    df.drop(["polymorphic_ctype", "id", "ligand_ptr"], axis=1, inplace=True)
    return df

def cap_and_read(ligand):
    """

    :param ligand: zb. "peptide", as string
    :return: returns pd with ligand_ptr, id, poly
    """
    return read_ligands(ligand.capitalize())


def read_buffer():
    model = get_model_by_name("Buffer")
    df = read_frame(model.objects.all())
    df.drop(["id"], axis=1, inplace=True)
    return df

def read_complex():
    model = get_model_by_name("complex")
    df = read_frame(model.objects.all(), ["sid","comment"])
    ligands_str = []
    for instance in model.objects.all():
        ligands_str.append(instance.ligands_str)
    df["complex_ligands"] = ligands_str
    return df

def read_steps(step):
    object_capitalized = step.capitalize()
    model = get_model_by_name(object_capitalized)
    df = read_frame(model.objects.all())
    df.drop(["id", "step_ptr"], axis=1, inplace=True)
    df.replace([np.NaN], [None], inplace=True)
    if "duration" in df:
        durations=[]
        for k,row in df.iterrows():
            durations.append(duration_to_string(row["duration"]))
        df["duration"]=durations
    if "temperature" in df:
        df['temperature'] = list(map(str, df['temperature'].values))
    df.replace(["None"],[None], inplace=True)


    return df

def read_ligand_batches(ligand_batch):
    object_capitalized = ligand_batch.capitalize()
    model = get_model_by_name(object_capitalized)
    if ligand_batch in ["peptideBatch","antibodyBatch", "complexBatch"]:
        df = read_frame(model.objects.all(), ["sid", "labeling", "concentration","concentration_unit","buffer__sid", "ph","purity", "produced_by__username",
                                          "production_date", "comment","stock",
                                          "ligand__sid"])
        df.replace([np.NaN], [None], inplace=True)
        df['purity'] = list(map(str, df['purity'].values))
        df['concentration'] = list(map(str, df['concentration'].values))


    elif ligand_batch == "virusBatch":
        df = read_frame(model.objects.all(),
                        ["sid", "labeling", "concentration","concentration_unit","buffer__sid", "ph","purity", "produced_by__username",
                                          "production_date", "comment",
                                          "ligand__sid", "passage_history","active","stock"])
        df.replace([np.NaN], [None], inplace=True)
        df['active'] = list(map(str, df['active'].values))
        df['passage_history'] = list(map(str, df['passage_history'].values))
        df['purity'] = list(map(str, df['purity'].values))
        df['concentration'] = list(map(str, df['concentration'].values) )



    elif ligand_batch == "bufferBatch":
        df = read_frame(model.objects.all(),
                        ["sid", "buffer__sid", "ph", "produced_by__username",
                         "production_date", "comment","stock"])
        df.replace([np.NaN], [None], inplace=True)

    df['buffer__sid'] = list(map(str, df['buffer__sid'].values))
    df['ph']=list(map(str, df['ph'].values))
    df['production_date']=list(map(str, df['production_date'].values))

    df.replace(["None"],[None], inplace=True)




    df = df.rename(columns={"ligand__sid":"ligand","produced_by__username":"produced_by","buffer__sid":"buffer"})


    return df


def get_or_create_raw_spots(**kwargs):
    RawSpot = apps.get_model("flutype","RawSpot")
    LigandBatch = apps.get_model("flutype","LigandBatch")

    lig_mob = read_gal_file(kwargs["lig_mob_path"])
    lig_fix = read_gal_file(kwargs["lig_fix_path"])
    lig_fix.rename(columns={"Name":"lig_fix_batch"}, inplace=True)
    spots = pd.merge(lig_fix,lig_mob,how='outer',on=['Row', 'Column'])
    spots.replace([np.NaN], [None], inplace=True)
    spots.rename(columns={"Name":"lig_mob_batch", "Row":"row","Column":"column"}, inplace=True)
    spots = spots[["row","column","lig_mob_batch","lig_fix_batch"]]
    spots["lig_mob_batch"]= spots["lig_mob_batch"].apply(lambda x: x if x == None else LigandBatch.objects.get_subclass(sid=x))
    #for k,spot in spots.iterrows():
    #    if spot["lig_fix_batch"] is not None:
    #        print(spot["lig_fix_batch"])
    #        LigandBatch.objects.get_subclass(sid=spot["lig_fix_batch"])
    spots["lig_fix_batch"]= spots["lig_fix_batch"].apply(lambda x: x if x == None else LigandBatch.objects.get_subclass(sid=x))


    #spots["lig_mob_batch"]= lig_mob["Name"].values

    spots["raw_spot_collection"]=kwargs["raw_spot_collection"]
    spots_dict = spots.to_dict('records')
    spots_instances = [RawSpot(**record) for record in spots_dict]

    #created = False
    #raw_spots = []
    #for k, spot in spots.iterrows():
    #    raw_spot, created = RawSpot.objects.get_or_create(**spot)
    #    raw_spots.append(raw_spot)
    with transaction.atomic():
      spo =  RawSpot.objects.bulk_create(spots_instances)
    #spo = [s.pk for s in spots_instances]
    return spo#, created


def  filter_for_class(list,class_name):
    Class = apps.get_model("flutype",class_name)
    return [x for x in list if isinstance(x, Class)]

def string_to_model(string, model):
    Instance = apps.get_model("flutype", model)
    inst, _ = Instance.objects.get_or_create(**ast.literal_eval(string))
    return inst

def create_spots(**kwargs):
    Spot = apps.get_model("flutype","Spot")
    intensities = read_gal_file(kwargs["intensities"])
    spots = pd.DataFrame(intensities["Name"].values, columns=["intensity"])


    spots["raw_spot"] = kwargs["raw_spot"]
    spots["spot_collection"] = kwargs["spot_collection"]


    if "std" in kwargs:
        std = read_gal_file(kwargs["std"])
        spots["std"] = std["Name"].values

    if "circle_quality" in kwargs:
        circle_quality = read_gal_file(kwargs["circle_quality"])
        spots["circle_quality"] = circle_quality["Name"].values

    if "circle" in kwargs:
        circle = read_gal_file(kwargs["circle"])
        spots["circle"] = circle["Name"].apply(string_to_model,args=("Circle",)).values

    if "square" in kwargs:
        square = read_gal_file(kwargs["square"])
        spots["square"] = square["Name"].apply(string_to_model,args=("Square",)).values

    spots_dict = spots.to_dict('records')

    spots_instances = [Spot(**record) for record in spots_dict]
    Spot.objects.bulk_create(spots_instances)


    #for k, spot in spots.iterrows():
    #    this_spot,_ = Spot.objects.get_or_create(raw_spot = spot["raw_spot"],
    #                                            spot_collection = spot["spot_collection"])


    #    if "std" in kwargs:
     #       this_spot.std = spot["std"]
    #        this_spot.save()

     #   if "circle_quality" in kwargs:
    #        this_spot.circle_quality = spot["circle_quality"]
    #        this_spot.save()

    #    this_spot.intensity = spot["intensity"]
    #    this_spot.save()


def meta_gal_file(type,file_src):
    hash_md =  md5sum(file_src)
    meta = {"type":type,"hash":hash_md,"sid":type + hash_md[:10]}
    return meta

def md5sum(src, length=io.DEFAULT_BUFFER_SIZE):
    md5 = hashlib.md5()
    with io.open(src, mode="rb") as fd:
        for chunk in iter(lambda: fd.read(length), b''):
            md5.update(chunk)
    return md5.hexdigest()

def get_unique_galfile(type, **kwargs):

    GalFile = apps.get_model("flutype", model_name="GalFile")
    this_gal = read_gal_file(kwargs["path"])
    max_name = 0
    for gal_file in GalFile.objects.filter(type=type):
        #updates name number
        result = re.search(type + '_(.*)', gal_file.sid)
        if int(result.group(1)) > max_name:
            max_name = int(result.group(1))

        #checks if equal
        df_gal = read_gal_file(gal_file.file.path)
        if df_gal.equals(this_gal):

            return gal_file, max_name

    return None, max_name


def read_gal_file(fpath):
    try:
        this_gal = pd.read_csv(fpath, sep='\t', index_col="ID", dtype=str)
        this_gal.replace([np.NaN], [None], inplace=True)
        this_gal.replace(["NO"], [None], inplace=True)
        this_gal.replace(["No"], [None], inplace=True)


    except:
        this_gal = pd.read_csv(fpath, sep='\t', index_col = 0,  dtype=str)
        this_gal = rows_and_cols_to_gal_file(this_gal)
        this_gal.replace([np.NaN], [None], inplace=True)
        #this_gal.replace(["NO"], [None], inplace=True)
        #this_gal.replace(["No"], [None], inplace=True)


    return this_gal

def read_gal_file_to_temporary_file(fpath):

    python_version = sys.version_info.major
    if python_version == 3:
        f = io.StringIO()
    else:
        f = tempfile.TemporaryFile()

    gal_file = read_gal_file(fpath)
    gal_file.to_csv(f, sep=str('\t'), index="True", encoding='utf-8')
    return f


def gal_file_to_rows_and_cols(this_gal):
    pass


def rows_and_cols_to_gal_file(this_gal):
    this_gal = this_gal.stack()
    id = range(1, 1 + len(this_gal.values))
    data = {"ID":id ,
            "Row": list(map(str,this_gal.index.get_level_values(0))),
            "Column": list(map(str,this_gal.index.get_level_values(1))),
            "Name":list(map(str, this_gal.values))
            }
    df = pd.DataFrame(data=data)
    df1 = df.set_index("ID")
    return df1



def create_study(**study_dic):

    Study = apps.get_model("flutype", model_name="Study")
    study, created = Study.objects.get_or_create(**study_dic["meta"])
    ##########################################################

def get_model_by_name(name):
    Model = apps.get_model("flutype",model_name=name)
    return Model

def get_user_or_none(user):
    if user is None:
            user = None
    else:
        user = User.objects.get(username__iexact=user)
    return user

def get_ligand_or_none(ligand):
    Ligand = apps.get_model("flutype", model_name="Ligand")
    if ligand is None:
            ligand = None
    else:
        #print(ligand)

        ligand = Ligand.objects.get(sid__iexact=ligand)


    return ligand

def get_buffer_or_none(buffer):
    Buffer = apps.get_model("flutype", model_name="Buffer")
    if buffer is None:
            buffer = None
    else:
        buffer = Buffer.objects.get(sid__iexact=buffer)
    return buffer

def get_duration_or_none(duration):
    if duration is None:
        duration = None
    else:
        dursplit = duration.split(":")
        duration = datetime.timedelta(days=int(dursplit[0]),
                                      hours=int(dursplit[1]),
                                      minutes=int(dursplit[2]),
                                      seconds=int(dursplit[3]))

    return duration

def duration_to_string(duration):
    if duration is None:
        duration = None
    else:
        seconds = duration.total_seconds()
        days = int(seconds // (3600*24))
        hours = int((seconds % (3600*24)) // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        duration = "{}:{}:{}:{}".format(days,hours,minutes,seconds)
    return duration




def get_or_create_object_from_dic(object_n, **kwargs):

    object_capitalized = object_n.capitalize()
    model = get_model_by_name(object_capitalized)
    object, created = model.objects.get_or_create(**kwargs)

    return object, created


def create_objects_from_df(object_n , object_df):
    for _, dict_single in object_df.iterrows():
        get_or_create_object_from_dic(object_n , **dict_single)



def fill_multiple_models_from_dict(object_dics):
    for object, object_df in object_dics.items():
        create_objects_from_df(object, object_df)




def datetimeformat(value, format='%H:%M / %d-%m-%Y'):
    return value.strftime(format)



def AbstractClassWithoutFieldsNamed(cls, *excl):
    if cls._meta.abstract:
        remove_fields = [f for f in cls._meta.local_fields if f.name in excl]
        for f in remove_fields:
            cls._meta.local_fields.remove(f)
        return cls
    else:
        raise Exception("Not an abstract model")