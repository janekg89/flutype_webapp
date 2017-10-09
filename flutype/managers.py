# models.py
from django.db import models

from flutype.helper import get_model_by_name ,get_ligand_or_none, get_user_or_none, get_duration_or_none,\
    add_raw_docs_model, get_or_create_raw_doc
from __future__ import absolute_import, print_function, unicode_literals

try:
   unicode = unicode
except NameError:
   # 'unicode' is undefined, must be Python 3
   str = str
   unicode = str
   bytes = bytes
   basestring = (str,bytes)
else:
   # 'unicode' exists, must be Python 2
   str = str
   unicode = unicode
   bytes = str
   basestring = basestring

class ProcessManager(models.Manager):
    def create(self, *args, **kwargs):
        pass

            #kwargs['type'] = HardwareType.objects.get(name=kwargs['type'])
        #super(HardwareManager, self).create(*args, **kwargs)


class LigandBatchManager(models.Manager):
    def create(self, *args, **kwargs):
        if "ligand" in kwargs and isinstance(kwargs['ligand'], basestring):
            kwargs['ligand'] =  get_ligand_or_none(kwargs['ligand'])
        if "produced_by" in kwargs and isinstance(kwargs['produced_by'], basestring):
            kwargs['produced_by'] =  get_user_or_none(kwargs['produced_by'])
        super(LigandBatchManager, self).create(*args,**kwargs)


class ComplexManager(models.Manager):
    def create(self, *args, **kwargs):
        if "complex_ligands" in kwargs and isinstance(kwargs['complex_ligands'], basestring):
            complex_ligands = kwargs["complex_ligands"]
            del kwargs["complex_ligands"]
            super(ComplexManager,self).create(*args,**kwargs)
            for ligand_sid in complex_ligands.split('-'):
                ligand = get_ligand_or_none(ligand_sid)
                self.complex_ligands.add(ligand)

class StepManager(models.Manager):
    def create(self, *args, **kwargs):
        if "duration" in kwargs and isinstance(kwargs['duration'], basestring):
            kwargs["duration"]=get_duration_or_none(kwargs['duration'])
            super(StepManager, self).create(*args,**kwargs)

class StudyManager(models.Manager):
    def create(self, *args, **kwargs):
        super(StudyManager, self).create(*args, **kwargs["meta"])
        if "raw_docs_fpaths" in kwargs:
            for fpath in kwargs["raw_docs_fpaths"]:
                raw_doc , _ = get_or_create_raw_doc(fpath=fpath)
                self.files.add(raw_doc)







