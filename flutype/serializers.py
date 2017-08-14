from rest_framework import serializers
from .models import RawSpotCollection, SpotCollection,RawSpot,LigandBatch, Ligand

class RawSpotCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawSpotCollection
'''
class LigandSerializer(serializers.ModelSerializer):
    ligand = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Ligand
        fields = ('ligand',)
'''


class LigandBatchSerializer(serializers.ModelSerializer):
    #ligand = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = LigandBatch
        fields = ('sid',)

class RawSpotSerializer(serializers.ModelSerializer):
    ligand1 = LigandBatchSerializer(read_only=True)
    ligand2 = LigandBatchSerializer(read_only=True)

    class Meta:
        model = RawSpot
        fields = ("ligand1","ligand2","column","row")