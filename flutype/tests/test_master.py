import os

from flutype.data_management.master import Master,Study, Measurement,MeasurementResult, BASEPATH

from django.test import TestCase
class MasterTestCase(TestCase):

    def setUp(self):
        self.path_master_test = os.path.join(BASEPATH,"master_new/")
        self.ma = Master(self.path_master_test)

    def test_master_init(self):
        #all studies
        self.assertEqual({'170929-tutorial'}, self.ma.study_sids)
        #steps
        self.assertEqual(set(self.ma.read_steps().keys()), set(self.ma.steps))
        self.assertEqual(set(self.ma.read_ligands().keys()), set(self.ma.ligands))
        ################################################################################################################
        ligand_batches = {"buffer_batch"}
        for ligand in self.ma.ligands:
            ligand_batches.add("{}_batch".format(ligand))
        self.assertEqual(set(self.ma.read_ligand_batches().keys()),ligand_batches)
        self.assertEqual(set(self.ma.read_studies().keys()),{'170929-tutorial'})

    def test_study_init(self):
        path_study = os.path.join(self.ma.path_study,next(iter(self.ma.study_sids)))
        st = Study(path_study)
        self.assertEqual(st.sid,"170929-tutorial")
        self.assertEqual(st.Master.study_sids,{'170929-tutorial'})
        self.assertEqual(st.raw_docs_fnames,{'tree.tar.gz'})
        self.assertEqual(st.measurement_sids, {'170929-tutorial-elisa-1',
                                               '170929-tutorial-microwell-1 ',
                                               '170929-tutorial-microarray-1'})
        self.assertEqual(set(st.meta.keys()),{'task', 'result'})
        self.assertEqual(set(st.read_measurements().keys()),{'170929-tutorial-elisa-1',
                                                             '170929-tutorial-microwell-1 ',
                                                             '170929-tutorial-microarray-1'})




    def test_measurement_init(self):
        path_study = os.path.join(self.ma.path_study,next(iter(self.ma.study_sids)))
        st = Study(path_study)
        path_measurement = os.path.join(st.path_measurements,next(iter(st.measurement_sids)))
        meas = Measurement(path_measurement)
        self.assertEqual(meas.sid,"170929-tutorial-elisa-1")
        self.assertEqual(meas.Study.sid,st.sid)
        self.assertEqual(set(meas.meta.keys()),{'measurement_type',
                                                'batch_sid',
                                                'user',
                                                'surface_substance',
                                                'manufacturer'})
        self.assertEqual(meas.raw_docs_fnames,set([]))
        self.assertEqual(next(iter(meas.read_results().keys())), "raw")
        self.assertEqual(set(meas.read().keys()),{"meta","lig_mob","lig_fix","steps","raw_docs","results"})


    def test_measurement_results_init(self):
        path_study = os.path.join(self.ma.path_study,next(iter(self.ma.study_sids)))
        st = Study(path_study)
        path_measurement = os.path.join(st.path_measurements, next(iter(st.measurement_sids)))
        meas = Measurement(path_measurement)
        path_measurement_results = os.path.join(meas.path_results,next(iter(meas.results_sids)))
        mea_result = MeasurementResult(path_measurement_results)
        self.assertEqual(mea_result.sid,"raw")
        self.assertEqual(set(mea_result.read().keys()),{'comment', 'intensity', 'processing_type'})











