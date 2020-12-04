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
from mocks import * # upas, mocks ...

######################################
######################################
######### TOGGLE PATCH ###############
######################################
###################################### 
do_patch = True # toggle patching for tests that can run independent of it

if do_patch:
    patch_ = patch
    patch_dict_ = patch.dict

else:
    patch_ = lambda *a, **k: lambda f: f
    patch_dict_ = lambda *a, **k: lambda f: f
######################################
######################################
######################################
######################################

class OTUSampleMetadataCorrelationTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('OTUSampleMetadataCorrelation'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [
                            {'service': 'OTUSampleMetadataCorrelation',
                             'method': 'please_never_use_it_in_production',
                             'method_params': []
                             }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = OTUSampleMetadataCorrelation(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        suffix = int(time.time() * 1000)
        cls.wsName = "test_ContigFilter_" + str(suffix)
        ret = cls.wsClient.create_workspace({'workspace': cls.wsName})  # noqa

    @classmethod
    def list_tests(cls):
        return [key for key, value in cls.__dict__.items() if type(key) == str and key.startswith('test') and callable(value)]

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')
        dec = '!!!' * 220
        print(dec, "DON'T FORGET TO SEE DIFF, HTML REPORT(S)", dec)
        print('Tests run (%d): %s' % (len(cls.list_tests()), cls.list_tests()))
        skipped_tests = list(set(all_tests) - set(cls.list_tests()))
        print('Tests skipped (%d): %s' % (len(skipped_tests), skipped_tests))


    def shortDescription(self):
        '''Override unittest using test*() docstrings in lieu of test*() method name in output summary'''
        return None

####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################

    # the 50by30 has original sample metadata names
    # the 17770by511 has normalized ones

    sample_metadata_50by30 ="Packing Depth Start (ft BGS)" #'packing_depth_start_ft_bgs' # 61
    sample_metadata_17770by511 = 'top_of_casing_stickup_ft' #"Top of Casing Stickup (ft)" # 68

    RDPClsf_taxonomy = "RDP Classifier taxonomy, conf=0.777, gene=silva_138_ssu, minWords=default"

####################################################################################################
############################### Taxonomy ###########################################################
####################################################################################################


    def _test_wTax(self, amp_mat_upa, sample_metadata, tax_rank, tax_field):
        ret = self.serviceImpl.run_OTUSampleMetadataCorrelation(
            self.ctx, {
                "amp_mat_upa": amp_mat_upa, 
                "sample_metadata": sample_metadata,
                "otu_params": {
                    "val_cutoff": None,
                    "sd_cutoff": None,
                    "tax_rank": tax_rank,
                    "tax_field": tax_field, # can be listed or not
                },
                "cor_params": {
                    "cor_cutoff": 0.1,
                    "cor_method": "kendall"
                },
                "p_adj_params": {
                    "p_adj_method": "BH",
                    "p_adj_cutoff": 0.9
                },
                'workspace_name': self.wsName,
        })


    ##########
    ##########
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
                    sample_metadata=self.sample_metadata_17770by511,
                    tax_rank=tax_rank,
                    tax_field=['taxonomy']
                )


    ##########
    ##########
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
                    sample_metadata=self.sample_metadata_50by30,
                    tax_rank=tax_rank,
                    tax_field=['taxonomy']
                )

    ##########
    ##########
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
                    sample_metadata=self.sample_metadata_17770by511,
                    tax_rank=tax_rank,
                    tax_field=[self.RDPClsf_taxonomy]
                )

    ##########
    ##########
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
                    sample_metadata=self.sample_metadata_50by30,
                    tax_rank=tax_rank,
                    tax_field=[self.RDPClsf_taxonomy]
                )



####################################################################################################
################################# Happy ############################################################
####################################################################################################

    ##########
    ##########
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: get_mock_dfu('enigma50by30'))
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_happy_small(self):
        '''
        '''
        ret = self.serviceImpl.run_OTUSampleMetadataCorrelation(
                self.ctx, {
                    "amp_mat_upa": enigma50by30,
                    "sample_metadata": self.sample_metadata_50by30,
                    "otu_params": {
                        "val_cutoff": None,
                        "sd_cutoff": None,
                        "tax_rank": None,
                        "tax_field": None,
                    },
                    "cor_params": {
                        "cor_cutoff": 0.01,
                        "cor_method": "kendall"
                    },
                    "p_adj_params": {
                        "p_adj_method": "BH",
                        "p_adj_cutoff": 0.9
                    },
                    'workspace_name': self.wsName,
            })


    ##########
    ##########
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: get_mock_dfu('enigma17770by511'))
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_happy_large_defaultParams(self):
        '''
        '''
        ret = self.serviceImpl.run_OTUSampleMetadataCorrelation(
                self.ctx, {
                    "amp_mat_upa": enigma17770by511,
                    "sample_metadata": self.sample_metadata_17770by511,
                    "otu_params": {
                        "val_cutoff": None,
                        "sd_cutoff": None,
                        "tax_rank": None,
                        "tax_field": None,
                    },
                    "cor_params": {
                        "cor_cutoff": 0.5,
                        "cor_method": "kendall"
                    },
                    "p_adj_params": {
                        "p_adj_method": "BH",
                        "p_adj_cutoff": 0.05
                    },
                    'workspace_name': self.wsName,
            })


    ##########
    ##########
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: get_mock_dfu('enigma17770by511'))
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_happy_large_customParams(self):
        '''
        '''
        ret = self.serviceImpl.run_OTUSampleMetadataCorrelation(
                self.ctx, {
                    "amp_mat_upa": enigma17770by511,
                    "sample_metadata": self.sample_metadata_17770by511,
                    "otu_params": {
                        "val_cutoff": 1,
                        "sd_cutoff": 1,
                        "tax_rank": 'genus',
                        "tax_field": ['taxonomy'],
                    },
                    "cor_params": {
                        "cor_cutoff": 0.001,
                        "cor_method": "spearman"
                    },
                    "p_adj_params": {
                        "p_adj_method": "bonferroni",
                        "p_adj_cutoff": 0.99
                    },
                    'workspace_name': self.wsName,
            })


####################################################################################################
################################# Knit exit ########################################################
####################################################################################################


    ##########
    ##########
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: get_mock_dfu('enigma50by30'))
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_small_nonePass_filterAmplicons(self):
        '''
        All amplicons filtered out by value/sd
        (Taxonomy can't eliminate all amplicons)
        '''
        ret = self.serviceImpl.run_OTUSampleMetadataCorrelation(
                self.ctx, {
                    "amp_mat_upa": enigma50by30,
                    "sample_metadata": self.sample_metadata_50by30,
                    "otu_params": {
                        "val_cutoff": 1e9,
                        "sd_cutoff": 1e9,
                        "tax_rank": None,
                        "tax_field": None,
                    },
                    "cor_params": {
                        "cor_cutoff": 0.5,
                        "cor_method": "kendall"
                    },
                    "p_adj_params": {
                        "p_adj_method": "BH",
                        "p_adj_cutoff": 0.05
                    },
                    'workspace_name': self.wsName,
            })



    ##########
    ##########
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: get_mock_dfu('enigma50by30'))
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_small_nonePass_succeedCor(self):
        pass # TODO test data for this



    ##########
    ##########
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: get_mock_dfu('enigma50by30'))
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_small_nonePass_filterCorPAdj(self):
        '''
        33 should not succeed in correlation testing
        Rest is filtered out
        '''
        ret = self.serviceImpl.run_OTUSampleMetadataCorrelation(
                self.ctx, {
                    "amp_mat_upa": enigma50by30,
                    "sample_metadata": self.sample_metadata_50by30,
                    "otu_params": {
                        "val_cutoff": None,
                        "sd_cutoff": None,
                        "tax_rank": None,
                        "tax_field": None,
                    },
                    "cor_params": {
                        "cor_cutoff": 0.9,
                        "cor_method": "pearson"
                    },
                    "p_adj_params": {
                        "p_adj_method": "BH",
                        "p_adj_cutoff": 0.05
                    },
                    'workspace_name': self.wsName,
            })

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
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
all_tests = []
for key, value in OTUSampleMetadataCorrelationTest.__dict__.items():
    if key.startswith('test') and callable(value):
        all_tests.append(key)

taxonomy_tests = ['test_large_wTax', 'test_large_wTax_RDPClsf', 'test_small_wTax', 'test_small_wTax_RDPClsf'] # TODO unit test tax parser
happy_path_tests = ['test_happy_large_defaultParams', 'test_happy_large_customParams', 'test_happy_small']
knit_exit_tests = ['test_small_nonePass_filterAmplicons', 'test_small_nonePass_filterCor', 'test_small_nonePass_filterCorPAdj', ]

run_tests = ['test_small_wTax']


for test in all_tests:
        if test not in run_tests:
            delattr(OTUSampleMetadataCorrelationTest, test)
            pass
