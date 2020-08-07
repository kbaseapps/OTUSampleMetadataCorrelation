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


##################################
##################################
testData_dir = '/kb/module/test/data'
##################################
##################################



####################################################################################################
################################ CI ################################################################
####################################################################################################
_17770_AmpMat = '48666/9/8' # accessory AmpliconMatrix to AmpliconSet
_17770_AttrMap = '48666/8/8' # accessory row AttributeMapping to AmpliconMatrix

first50 = "48402/9/2" # AmpliconSet containing first 50 of 17770 entries. row AttributeMapping has all 1770 entries (?)

secret_AmpMat = '49926/5/2' # AmpliconMatrix. No row AttributeMapping. Do not share

secret_wRDP_AmpMat = '49926/5/12' # AmpliconMatrix. With row AttributeMapping with taxonomy. Do not share
secret_wRDP_colAttrMap = '49226/8/1' # col AttributeMapping. Do not share


####################################################################################################
############################# appdev ###############################################################
####################################################################################################

_17770_50samples_AmpMat = "45688/2/3"
_17770_50samples_colAttrMap = "45688/3/1"

####################################################################################################
########################## dummy ###################################################################
####################################################################################################
dummy_10by8_AmpMat_noRowAttrMap = 'dummy/10by8/AmpMat_noRowAttrMap'
dummy_10by8_AmpMat_wRowAttrMap = 'dummy/10by8/AmpMat_wRowAttrMap'
dummy_10by8_AttrMap = 'dummy/10by8/AttrMap'







def get_mock_dfu(dataset):
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

        upa = params['object_refs'][0]
        flnm = {
            _17770_AmpMat: 'get_objects_AmpliconMatrix.json',
            _17770_AttrMap: 'get_objects_AttributeMapping.json',
            _17770_50samples_AmpMat: 'get_objects_AmpliconMatrix.json',
            _17770_50samples_colAttrMap: 'get_objects_AttributeMapping.json',
            secret_AmpMat: 'get_objects_AmpliconMatrix.json',
            dummy_10by8_AmpMat_wRowAttrMap: 'get_objects_AmpliconMatrix_wRowAttrMap.json',
            dummy_10by8_AmpMat_noRowAttrMap: 'get_objects_AmpliconMatrix_noRowAttrMap.json',
            dummy_10by8_AttrMap: 'get_objects_AttributeMapping.json',
            }[upa]
        flpth = os.path.join(testData_dir, 'by_dataset_input', dataset, 'get_objects', flnm)

        with open(flpth) as f:
            obj = json.load(f)

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




####################################################################################################
########### allow all UPAs, including _17770* variables, to be imported with * #####################
####################################################################################################
substr_l =['17770', 'first50', 'secret', 'dummy', 'mock', 'testData_dir'] 
__all__ = [x for x in dir() if any([substr in x for substr in substr_l])]




