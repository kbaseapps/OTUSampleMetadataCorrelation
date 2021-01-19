import os
import time
import unittest
from unittest.mock import patch
from configparser import ConfigParser

from OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl import OTUSampleMetadataCorrelation
from OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationServer import MethodContext
from OTUSampleMetadataCorrelation.authclient import KBaseAuth as _KBaseAuth
from installed_clients.WorkspaceClient import Workspace

from OTUSampleMetadataCorrelation.util.dprint import dprint
from OTUSampleMetadataCorrelation.util.kbase_obj import AmpliconMatrix
from data import * 
import config as cfg
from config import do_patch, patch_, patch_dict_



class TestCase(cfg.BaseTest):

####################################################################################################
####################################################################################################
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: get_mock_dfu('enigma50by30'))
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_nonePass_prelimFilter(self):
        '''
        All amplicons filtered out by value/sd
        (Taxonomy can't eliminate all amplicons)
        '''
        ret = cfg.get_serviceImpl().run_OTUSampleMetadataCorrelation(
                cfg.ctx, {
                    "amp_mat_upa": enigma50by30,
                    "sample_metadata": sample_metadata_50by30,
                    "amp_params": {
                        "val_cutoff": 1e9,
                        "sd_cutoff": 1e9,
                        "tax_rank": None,
                        "tax_field": None,
                    },
                    "cor_params": {
                        "cor_cutoff": 0.5,
                        "cor_method": "kendall",
                        "p_adj_method": "BH",
                        "p_adj_cutoff": 0.05
                    },
                    'workspace_name': self.wsName,
            })



####################################################################################################
####################################################################################################
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_nonePass_succeedCor(self):
        # get obj with all 1s
        with patch.dict( 
            'OTUSampleMetadataCorrelation.util.kbase_obj.Var',
            values={'dfu': get_mock_dfu('enigma50by30')}
        ):
            obj = AmpliconMatrix(enigma50by30).obj
            obj['data']['values'] = [[1 for j in range(30)] for i in range(50)] # all 1s
            
        # integreate all-1s version into mock dfu
        dfu = get_mock_dfu(
            'enigma50by30', 
            replace_obj={enigma50by30: obj}
        )

        # run with all-1s-obj patched in
        with patch( 
            'OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil',
            new=lambda *a, **kw: dfu
        ):
            ret = cfg.get_serviceImpl().run_OTUSampleMetadataCorrelation(
                    cfg.ctx, {
                        "amp_mat_upa": enigma50by30,
                        "sample_metadata": sample_metadata_50by30,
                        "amp_params": {
                            "val_cutoff": None,
                            "sd_cutoff": None,
                            "tax_rank": None,
                            "tax_field": None,
                        },
                        "cor_params": {
                            "cor_cutoff": 0,
                            "cor_method": "pearson",
                            "p_adj_method": "bonferroni",
                            "p_adj_cutoff": 1
                        },
                        'workspace_name': self.wsName,
                })



####################################################################################################
####################################################################################################
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: get_mock_dfu('enigma50by30'))
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_nonePass_filterCor(self):
        ret = cfg.get_serviceImpl().run_OTUSampleMetadataCorrelation(
                cfg.ctx, {
                    "amp_mat_upa": enigma50by30,
                    "sample_metadata": sample_metadata_50by30,
                    "amp_params": {
                        "val_cutoff": None,
                        "sd_cutoff": None,
                        "tax_rank": None,
                        "tax_field": None,
                    },
                    "cor_params": {
                        "cor_cutoff": 1,
                        "cor_method": "spearman",
                        "p_adj_method": "BH",
                        "p_adj_cutoff": 0.05
                    },
                    'workspace_name': self.wsName,
            })


####################################################################################################
####################################################################################################
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: get_mock_dfu('enigma50by30'))
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_nonePass_filterPAdj(self):
        ret = cfg.get_serviceImpl().run_OTUSampleMetadataCorrelation(
                cfg.ctx, {
                    "amp_mat_upa": enigma50by30,
                    "sample_metadata": sample_metadata_50by30,
                    "amp_params": {
                        "val_cutoff": None,
                        "sd_cutoff": None,
                        "tax_rank": None,
                        "tax_field": None,
                    },
                    "cor_params": {
                        "cor_cutoff": 0,
                        "cor_method": "pearson",
                        "p_adj_method": "BH",
                        "p_adj_cutoff": 0
                    },
                    'workspace_name': self.wsName,
            })

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    @classmethod
    def list_tests(cls):
        return [key for key, value in cls.__dict__.items() if type(key) == str and key.startswith('test') and callable(value)]

    @classmethod
    def tearDownClass(cls):
        super(cls, cls).tearDownClass()

        dec = '!!!' * 220
        print(dec, "DON'T FORGET TO SEE DIFF, HTML REPORT(S)", dec)
        print('Tests run (%d): %s' % (len(cls.list_tests()), cls.list_tests()))
        skipped_tests = list(set(all_tests) - set(cls.list_tests()))
        print('Tests skipped (%d): %s' % (len(skipped_tests), skipped_tests))




#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
all_tests = []
for key, value in TestCase.__dict__.items():
    if key.startswith('test') and callable(value):
        all_tests.append(key)

knit_exit_tests = ['test_nonePass_prelimFilter', 'test_nonePass_filterCor', 'test_nonePass_filterCor',  'test_nonePass_filterPAdj']

run_tests = ['test_nonePass_succeedCor']


for test in all_tests:
        if test not in run_tests:
            #delattr(TestCase, test)
            pass
