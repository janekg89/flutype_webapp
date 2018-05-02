import os
from django.test import TransactionTestCase
from django.test import tag

from flutype.data_management.master import Master,Study, Measurement,MeasurementResult, BASEPATH

MASTERPATH = os.path.join(BASEPATH, "master_test")

class MasterTestCase(TransactionTestCase):

    def setUp(self):
        self.ma = Master(MASTERPATH)

    def test_master_init(self):
        #all studies
        self.assertEqual({'tutorial_2017_09_29'}, self.ma.study_sids)
        #steps
        self.assertEqual(set(self.ma.read_steps().keys()), set(self.ma.steps))
        self.assertEqual(set(self.ma.read_ligands().keys()), set(self.ma.ligands))
        ################################################################################################################
        ligand_batches = {"bufferBatch", "complexBatch"}
        for ligand in self.ma.ligands:
            ligand_batches.add("{}Batch".format(ligand))
        self.assertEqual(set(self.ma.read_ligand_batches().keys()),ligand_batches)
        self.assertEqual(set(self.ma.read_studies().keys()),{'tutorial_2017_09_29'})


    def test_study_init(self):
        path_study = os.path.join(self.ma.path_study,next(iter(self.ma.study_sids)))
        st = Study(path_study)
        self.assertEqual(st.sid,"tutorial_2017_09_29")
        self.assertEqual(st.Master.study_sids,{'tutorial_2017_09_29'})
        self.assertEqual(st.raw_docs_fnames,{'170929-tutorial.tar.gz','test_file_1.txt'})
        self.assertEqual(st.measurement_sids, {'170929-tutorial-elisa-1',
                                               '170929-tutorial-microwell-1'})
        self.assertEqual(set(st.meta.keys()),{'comment', 'user','description','date','hidden','status'})
        self.assertEqual(set(st.read_measurements().keys()),{'170929-tutorial-elisa-1',
                                                             '170929-tutorial-microwell-1',
                                                            })




    def test_measurement_init(self):
        path_study = os.path.join(self.ma.path_study,next(iter(self.ma.study_sids)))
        st = Study(path_study)
        path_measurement = os.path.join(st.path_measurements,"170929-tutorial-elisa-1")
        meas = Measurement(path_measurement)
        self.assertEqual(meas.sid,"170929-tutorial-elisa-1")
        self.assertEqual(meas.Study.sid,st.sid)
        self.assertEqual(set(meas.meta.keys()),{'measurement_type',
                                                'batch_sid',
                                                'manufacturer',
                                                'hidden',
                                                'comment',
                                                'functionalization',

                                                })
        self.assertEqual(next(iter(meas.read_results().keys())), "raw")
        self.assertEqual(set(meas.read().keys()),{"meta","lig_mob_path","lig_fix_path","steps_path","results"})


    def test_measurement_results_init(self):
        path_study = os.path.join(self.ma.path_study,next(iter(self.ma.study_sids)))
        st = Study(path_study)
        path_measurement = os.path.join(st.path_measurements,"170929-tutorial-elisa-1")
        meas = Measurement(path_measurement)
        path_measurement_results = os.path.join(meas.path_results,next(iter(meas.results_sids)))
        mea_result = MeasurementResult(path_measurement_results)
        self.assertEqual(mea_result.sid,"raw")
        self.assertEqual(set(mea_result.read().keys()),{'intensities', 'meta'})













