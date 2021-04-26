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
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: mock_dfu)
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: mock_kbr)
    def test_nonePass_prelimFilter(self):
        '''
        All amplicons filtered out by value/sd
        (Taxonomy can't eliminate all amplicons)
        '''
        ret = self.serviceImpl.run_OTUSampleMetadataCorrelation(
                self.ctx, {
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
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: mock_kbr)
    def test_nonePass_succeedCor(self):
        # get obj with all 1s
        with patch.dict( 
            'OTUSampleMetadataCorrelation.util.kbase_obj.Var',
            values={'dfu': mock_dfu}
        ):
            obj = AmpliconMatrix(enigma50by30).obj
            obj['data']['values'] = [[1 for j in range(30)] for i in range(50)] # all 1s
            
        # integreate all-1s version into mock dfu
        dfu = get_mock_dfu(
            replace_obj={enigma50by30: obj}
        )

        # run with all-1s-obj patched in
        with patch( 
            'OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil',
            new=lambda *a, **kw: dfu
        ):
            ret = self.serviceImpl.run_OTUSampleMetadataCorrelation(
                    self.ctx, {
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
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: mock_dfu)
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: mock_kbr)
    def test_nonePass_filterCor(self):
        ret = self.serviceImpl.run_OTUSampleMetadataCorrelation(
                self.ctx, {
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
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: mock_dfu)
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: mock_kbr)
    def test_nonePass_filterPAdj(self):
        ret = self.serviceImpl.run_OTUSampleMetadataCorrelation(
                self.ctx, {
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
    @classmethod
    def tearDownClass(cls):
        super(cls, cls).tearDownClass()

        dec = '!!!' * 220
        print(dec, "DON'T FORGET TO SEE DIFF, HTML REPORT(S)", dec)

