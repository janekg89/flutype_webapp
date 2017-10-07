from rest_framework import serializers
from flutype.models import (Peptide,
                            PeptideBatch,
                            Virus,
                            Complex,
                            ComplexBatch,
                            VirusBatch,
                            Antibody,
                            AntibodyBatch,
                            Ligand,
                            LigandBatch,
                            RawSpotCollection,
                            SpotCollection,
                            RawSpot,
                            Spot,
                            Spotting,
                            Quenching,
                            Incubating,
                            Washing,
                            Drying,
                            Scanning,
                            Blocking,
                            ProcessStep,
                            Process,
                            GalFile,
                            Step,
                            Study
                            )

class StudySerializer(serializers.ModelSerializer):
    class Meta:
        model =Study
        fields = []