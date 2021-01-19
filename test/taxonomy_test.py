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
from data import * 
import config as cfg
from config import patch_, patch_dict_



class TestCase(cfg.BaseTest):



    def _test_wTax(self, amp_mat_upa, sample_metadata, tax_rank, tax_field):
        ret = cfg.get_serviceImpl().run_OTUSampleMetadataCorrelation(
            cfg.ctx, {
                "amp_mat_upa": amp_mat_upa, 
                "sample_metadata": sample_metadata,
                "amp_params": {
                    "val_cutoff": None,
                    "sd_cutoff": None,
                    "tax_rank": tax_rank,
                    "tax_field": tax_field, # can be listed or not
                },
                "cor_params": {
                    "cor_cutoff": 0.1,
                    "cor_method": "kendall",
                    "p_adj_method": "BH",
                    "p_adj_cutoff": 0.9
                },
                'workspace_name': self.wsName,
        })

####################################################################################################
####################################################################################################
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: get_mock_dfu('enigma17770by511'))
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_large_wTax(self):
        tax_ranks = [
            #'domain', 'phylum', 'class', 'order', 'family', 'genus', 'species',
            'family',
        ]

        for tax_rank in tax_ranks:
            with self.subTest(tax_rank=tax_rank):
                self._test_wTax(
                    amp_mat_upa=enigma17770by511,
                    sample_metadata=sample_metadata_17770by511,
                    tax_rank=tax_rank,
                    tax_field=['taxonomy']
                )


####################################################################################################
####################################################################################################
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: get_mock_dfu('enigma50by30'))
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_small_wTax(self):
        tax_ranks = [
            'domain', 'phylum', 'class', 'order', 'family', 'genus', 'species',
        ]

        for tax_rank in tax_ranks:
            with self.subTest(tax_rank=tax_rank):
                self._test_wTax(
                    amp_mat_upa=enigma50by30,
                    sample_metadata=sample_metadata_50by30,
                    tax_rank=tax_rank,
                    tax_field=['taxonomy']
                )

####################################################################################################
####################################################################################################
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: get_mock_dfu('enigma17770by511_RDPClsf'))
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_large_wTax_RDPClsf(self):
        tax_ranks = [
            #'domain', 'phylum', 'class', 'order', 'family', 'genus', 'species',
            'order',
        ]

        for tax_rank in tax_ranks:
            with self.subTest(tax_rank=tax_rank):
                self._test_wTax(
                    amp_mat_upa=enigma17770by511_RDPClsf,
                    sample_metadata=sample_metadata_17770by511,
                    tax_rank=tax_rank,
                    tax_field=[RDPClsf_taxonomy]
                )

####################################################################################################
####################################################################################################
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: get_mock_dfu('enigma50by30_RDPClsf'))
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_small_wTax_RDPClsf(self):
        tax_ranks = [
            'domain', 'phylum', 'class', 'order', 'family', 'genus', 'species',
        ]

        for tax_rank in tax_ranks:
            with self.subTest(tax_rank=tax_rank):
                self._test_wTax(
                    amp_mat_upa=enigma50by30_RDPClsf,
                    sample_metadata=sample_metadata_50by30,
                    tax_rank=tax_rank,
                    tax_field=[RDPClsf_taxonomy]
                )

                
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

taxonomy_tests = ['test_large_wTax', 'test_large_wTax_RDPClsf', 'test_small_wTax', 'test_small_wTax_RDPClsf'] # TODO unit test tax parser

run_tests = ['test_small_wTax']


for test in all_tests:
        if test not in run_tests:
            #delattr(TestCase, test)
            pass

