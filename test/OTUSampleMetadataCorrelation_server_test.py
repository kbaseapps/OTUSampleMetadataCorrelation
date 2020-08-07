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
    patch_ = lambda *a, **kwargs: lambda f: f
    patch_dict_ = lambda *a, **kwargs: lambda f: f
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
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.DataFileUtil', new=lambda u: get_mock_dfu('17770_50samples'))
    #@patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.run_check', new=get_mock_run_check('17770_50samples'))
    @patch_('OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl.KBaseReport', new=lambda u: get_mock_kbr())
    def test_your_method(self):
        ret = self.serviceImpl.run_OTUSampleMetadataCorrelation(
                self.ctx, {
                    "amp_mat_upa": "45688/2/3",
                    "col_attrmap_upa": "45688/3/1",
                    "row_attrmap_upa": None,
                    "sample_metadata": ["Top of Casing Stickup (ft)"],
                    "otu_params": {
                        "abund_cutoff": None,
                        "sd_cutoff": None,
                        "freq_cutoff": None,
                        "tax_rank": "None"
                    },
                    "cor_params": {
                        "cor_cutoff": 0.6,
                        "cor_method": "pearson"
                    },
                    "p_adj_params": {
                        "p_adj_method": "BH",
                        "p_adj_cutoff": 0.05
                    },
                    'workspace_name': self.wsName,
            })
