# models.py
from django.db import models

from flutype.helper import get_model_by_name ,get_ligand_or_none


class ProcessManager(models.Manager):
    def create(self, *args, **kwargs):
        pass

            #kwargs['type'] = HardwareType.objects.get(name=kwargs['type'])
        #super(HardwareManager, self).create(*args, **kwargs)


class LigandBatchManager(models.Manager):
    def create(self, *args, **kwargs):
        if "ligand" in kwargs and isinstance(kwargs['type'], basestring):
            kwargs['ligand'] =  get_ligand_or_none(kwargs['ligand'])
            super(LigandBatchManager, self).create(*args, **kwargs)




