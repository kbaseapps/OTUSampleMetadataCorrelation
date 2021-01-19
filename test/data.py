from unittest.mock import create_autospec
import os
import sys
from shutil import rmtree, copytree
import logging
import json

from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.KBaseReportClient import KBaseReport

from OTUSampleMetadataCorrelation.OTUSampleMetadataCorrelationImpl import run_check
from OTUSampleMetadataCorrelation.util.dprint import dprint
from OTUSampleMetadataCorrelation.util.config import Var




####################################################################################################
############################## attributes ##########################################################
####################################################################################################
# the 50by30 has original sample metadata names
# the 17770by511 has normalized ones
sample_metadata_50by30 ="Packing Depth Start (ft BGS)" #'packing_depth_start_ft_bgs' # 61
sample_metadata_17770by511 = 'top_of_casing_stickup_ft' #"Top of Casing Stickup (ft)" # 68
RDPClsf_taxonomy = "RDP Classifier taxonomy, conf=0.777, gene=silva_138_ssu, minWords=default"



####################################################################################################
################################ CI ################################################################
####################################################################################################
enigma50by30_noAttrMaps_noSampleSet = '55136/4/1' # AmpliconMatrix

enigma50by30 = '55136/15/1' # AmpliconMatrix
enigma50by30_rowAttrMap = '55136/11/1'
enigma50by30_colAttrMap = '55136/14/1'

enigma50by30_noSampleSet = '55136/17/1' # AmpliconMatrix

enigma17770by511 = '55136/26/1' # AmpliconMatrix
enigma17770by511_rowAttrMap = '55136/19/1'
enigma17770by511_colAttrMap = '55136/25/1'

enigma50by30_RDPClsf = '55136/28/1' # AmpMat
enigma50by30_RDPClsf_rowAttrMap = '55136/11/2' # AttrMap

enigma17770by511_RDPClsf = '55628/25/2'
enigma17770by511_RDPClsf_rowAttrMap = '55628/27/5'

####################################################################################################
########################## dummy ###################################################################
####################################################################################################
#dummy_10by8_AmpMat_noRowAttrMap = 'dummy/10by8/AmpMat_noRowAttrMap'
#dummy_10by8_AmpMat_wRowAttrMap = 'dummy/10by8/AmpMat_wRowAttrMap'
dummy10by8 = 'dummy/10by8/AmpMat'
dummy10by8_rowAttrMap = 'dummy/10by8/rowAttrMap'



####################################################################################################
####################################################################################################
####################################################################################################


testData_dir = '/kb/module/test/data'


def get_mock_dfu(dataset, replace_obj=None):
    '''
    Avoid lengthy `get_objects` and `save_objects`
    '''
    mock_dfu = create_autospec(DataFileUtil, instance=True)

    ##
    ## mock `save_objects`
    def mock_dfu_save_objects(params):
        params_str = str(params)
        if len(params_str) > 100: params_str = params_str[:100] + ' ...'
        logging.info('Mocking `dfu.save_objects` with `params=%s`' % params_str)

        return [['-1111', 1, 2, 3, '-1111', 5, '-1111']] # UPA made from pos 6/0/4
    
    mock_dfu.save_objects.side_effect = mock_dfu_save_objects

    ##
    ## mock `get_objects`
    def mock_dfu_get_objects(params):
        logging.info('Mocking `dfu.get_objects` with `params=%s`' % str(params))

        upa = params['object_refs'][0].split(';')[-1]
        flnm = {
            enigma50by30: 'AmpliconMatrix.json',
            enigma50by30_rowAttrMap : 'row_AttributeMapping.json',
            enigma50by30_colAttrMap: 'col_AttributeMapping.json',
            enigma50by30_RDPClsf: 'AmpliconMatrix.json',
            enigma50by30_RDPClsf_rowAttrMap: 'row_AttributeMapping.json',
            enigma50by30_noSampleSet: 'AmpliconMatrix.json',
            enigma50by30_noAttrMaps_noSampleSet : 'AmpliconMatrix.json',
            enigma17770by511: 'AmpliconMatrix.json',
            enigma17770by511_rowAttrMap: 'row_AttributeMapping.json',
            enigma17770by511_colAttrMap: 'col_AttributeMapping.json',
            enigma17770by511_RDPClsf: 'AmpliconMatrix.json',
            enigma17770by511_RDPClsf_rowAttrMap: 'row_AttributeMapping.json',
            dummy10by8: 'AmpliconMatrix.json',
            dummy10by8_rowAttrMap: 'row_AttributeMapping.json',
            #dummy10by8_colAttrMap: 'col_AttributeMapping.json',
        }[upa]
        flpth = os.path.join(testData_dir, 'by_dataset_input', dataset, 'get_objects', flnm)

        with open(flpth) as f:
            obj = json.load(f)

        # swap in arg obj
        if replace_obj is not None:
            upa = params['object_refs'][0] # this only works for 1 input UPA
            if upa in replace_obj:
                obj['data'][0]['data'] = replace_obj[upa]

        return obj

    mock_dfu.get_objects.side_effect = mock_dfu_get_objects

    return mock_dfu


def get_mock_run_check(dataset):
    '''
    Avoid expensive runs of tool
    Copy over `Var.out_dir`
    '''
    mock_run_check = create_autospec(run_check)

    # side effect
    def mock_run_check_(cmd):
        logging.info('Mocking running cmd `%s`' % cmd)

        # test data
        src_drpth = os.path.join(testData_dir, 'by_dataset_input', dataset, 'return/output')

        # check if it already exists
        # since app may create it before run, and
        # since `check_run` is called twice in this app
        if os.path.exists(Var.out_dir):
            rmtree(Var.out_dir)
        copytree(src_drpth, Var.out_dir)


    mock_run_check.side_effect = mock_run_check_

    return mock_run_check


def get_mock_kbr(dataset=None): 
    '''
    Avoid lengthy `create_extended_report`

    Does not use input currently
    '''

    mock_kbr = create_autospec(KBaseReport, instance=True) 

    # mock `create_extended_report`
    def mock_create_extended_report(params):
        logging.info('Mocking `kbr.create_extended_report`')

        return {
            'name': 'kbr_mock_name',
            'ref': 'kbr/mock/ref',
        }

    mock_kbr.create_extended_report.side_effect = mock_create_extended_report
    
    return mock_kbr






