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
        ret = self.serviceImpl.run_OTUSampleMetadataCorrelation(
            self.ctx, {
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
    @unittest.skip('large, private')
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
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: mock_dfu)
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: mock_kbr)
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
    @unittest.skip('large, private')
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
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: mock_dfu)
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: mock_kbr)
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


    @classmethod
    def tearDownClass(cls):
        super(cls, cls).tearDownClass()

        dec = '!!!' * 220
        print(dec, "DON'T FORGET TO SEE DIFF, HTML REPORT(S)", dec)

