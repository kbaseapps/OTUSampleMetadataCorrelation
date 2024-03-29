# -*- coding: utf-8 -*-
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
from data import * # upas, mocks ...
import config as cfg
from config import do_patch, patch_, patch_dict_



class TestCase(cfg.BaseTest):


####################################################################################################
####################################################################################################
    @unittest.skip('large, private')
    def test_large_defaultParams(self):
        '''
        '''
        ret = self.serviceImpl.run_OTUSampleMetadataCorrelation(
                self.ctx, {
                    "amp_mat_upa": enigma17770by511,
                    "sample_metadata": sample_metadata_17770by511,
                    "amp_params": {
                        "val_cutoff": None,
                        "sd_cutoff": None,
                        "tax_rank": None,
                        "tax_field": None,
                    },
                    "cor_params": {
                        "cor_cutoff": 0.5,
                        "cor_method": "kendall",
                        "p_adj_method": "BH",
                        "p_adj_cutoff": 0.05,
                    },
                    'workspace_name': self.wsName,
            })


####################################################################################################
####################################################################################################
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: mock_dfu)
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: mock_kbr)
    def test_small_2_results(self):
        '''
        '''
        ret = self.serviceImpl.run_OTUSampleMetadataCorrelation(
                self.ctx, {
                    "amp_mat_upa": enigma50by30,
                    "sample_metadata": sample_metadata_50by30,
                    "amp_params": {
                        "val_cutoff": 1,
                        "sd_cutoff": 1,
                        "tax_rank": 'genus',
                        "tax_field": ['taxonomy'],
                    },
                    "cor_params": {
                        "cor_cutoff": 0.5208,
                        "cor_method": "kendall",
                        "p_adj_method": "bonferroni",
                        "p_adj_cutoff": 0.99999999,
                    },
                    'workspace_name': self.wsName,
            })



####################################################################################################
####################################################################################################
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: mock_dfu)
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: mock_kbr)
    def test_small_3_results(self):
        '''
        '''
        ret = self.serviceImpl.run_OTUSampleMetadataCorrelation(
                self.ctx, {
                    "amp_mat_upa": enigma50by30,
                    "sample_metadata": sample_metadata_50by30,
                    "amp_params": {
                        "val_cutoff": 1,
                        "sd_cutoff": 1,
                        "tax_rank": 'genus',
                        "tax_field": ['taxonomy'],
                    },
                    "cor_params": {
                        "cor_cutoff": 0.503,
                        "cor_method": "kendall",
                        "p_adj_method": "bonferroni",
                        "p_adj_cutoff": 1,
                    },
                    'workspace_name': self.wsName,
            })

####################################################################################################
####################################################################################################
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: mock_dfu)
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: mock_kbr)
    def test_small_5_results(self):
        '''
        '''
        ret = self.serviceImpl.run_OTUSampleMetadataCorrelation(
                self.ctx, {
                    "amp_mat_upa": enigma50by30,
                    "sample_metadata": sample_metadata_50by30,
                    "amp_params": {
                        "val_cutoff": 1,
                        "sd_cutoff": 1,
                        "tax_rank": 'genus',
                        "tax_field": ['taxonomy'],
                    },
                    "cor_params": {
                        "cor_cutoff": 0.36,
                        "cor_method": "kendall",
                        "p_adj_method": "bonferroni",
                        "p_adj_cutoff": 0.99999999,
                    },
                    'workspace_name': self.wsName,
            })
####################################################################################################
####################################################################################################
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: mock_dfu)
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: mock_kbr)
    def test_small(self):
        '''
        '''
        ret = self.serviceImpl.run_OTUSampleMetadataCorrelation(
                self.ctx, {
                    "amp_mat_upa": enigma50by30,
                    "sample_metadata": sample_metadata_50by30,
                    "amp_params": {
                        "val_cutoff": None,
                        "sd_cutoff": None,
                        "tax_rank": 'genus',
                        "tax_field": ['taxonomy'],
                    },
                    "cor_params": {
                        "cor_cutoff": 0.01,
                        "cor_method": "pearson",
                        "p_adj_method": "BH",
                        "p_adj_cutoff": 0.9,
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
"""
Stuff to test:
    * unit test invalid metadata, tax table, amplicon matrix (different ways of invalid, numeric and missing)
    * unit tests?
    * unit test tax pooling
    * nothing passes correlation filtering (integration)
    * rand param gen?

TODOs:
    * show correlation filtering table even if nothing passes at some point?
"""


