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
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: get_mock_dfu('enigma17770by511'))
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_happy_large_defaultParams(self):
        '''
        '''
        ret = cfg.get_serviceImpl().run_OTUSampleMetadataCorrelation(
                cfg.ctx, {
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
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: get_mock_dfu('enigma17770by511'))
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_happy_large_customParams(self):
        '''
        '''
        ret = cfg.get_serviceImpl().run_OTUSampleMetadataCorrelation(
                cfg.ctx, {
                    "amp_mat_upa": enigma17770by511,
                    "sample_metadata": sample_metadata_17770by511,
                    "amp_params": {
                        "val_cutoff": 1,
                        "sd_cutoff": 1,
                        "tax_rank": 'genus',
                        "tax_field": ['taxonomy'],
                    },
                    "cor_params": {
                        "cor_cutoff": 0.001,
                        "cor_method": "spearman",
                        "p_adj_method": "bonferroni",
                        "p_adj_cutoff": 0.99,
                    },
                    'workspace_name': self.wsName,
            })



####################################################################################################
####################################################################################################
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: get_mock_dfu('enigma50by30'))
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_happy_small(self):
        '''
        '''
        ret = cfg.get_serviceImpl().run_OTUSampleMetadataCorrelation(
                cfg.ctx, {
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
                        "cor_method": "kendall",
                        "p_adj_method": "BH",
                        "p_adj_cutoff": 0.9,
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

happy_path_tests = ['test_happy_large_defaultParams', 'test_happy_large_customParams', 'test_happy_small']

run_tests = ['test_happy_small']


for test in all_tests:
        if test not in run_tests:
            #delattr(TestCase, test)
            pass
