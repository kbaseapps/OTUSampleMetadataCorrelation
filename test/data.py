from unittest.mock import create_autospec
import os
import sys
from shutil import rmtree, copytree
import logging
import json
from pathlib import Path

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
sample_metadata_50by30 = 'packing_depth_start_ft_bgs' #"Packing Depth Start (ft BGS)" # 61
sample_metadata_17770by511 = 'top_of_casing_stickup_ft' #"Top of Casing Stickup (ft)" # 68
RDPClsf_taxonomy = "RDP Classifier taxonomy, conf=0.777, gene=silva_138_ssu, minWords=default"



####################################################################################################
################################ CI ################################################################
####################################################################################################
enigma50by30 = '61042/5/1'
enigma50by30_RDPClsf = '61042/8/1'

"""
enigma50by30 = '55136/15/1' # AmpliconMatrix
enigma50by30_RDPClsf = '55136/28/1' # AmpMat
"""

enigma17770by511 = '55136/26/1' # AmpliconMatrix
enigma17770by511_RDPClsf = '55628/25/2'



####################################################################################################
####################################################################################################
####################################################################################################



TEST_DATA_DIR = '/kb/module/test/data'
GET_OBJECTS_DIR = TEST_DATA_DIR + '/get_objects'
GET_OBJECT_INFO3_DIR = TEST_DATA_DIR + '/get_object_info3'
FASTA_DIR = TEST_DATA_DIR + '/fasta'
WORK_DIR = '/kb/module/work/tmp'
CACHE_DIR = WORK_DIR + '/cache_test_data'

## MOCK DFU ##

def get_mock_dfu(replace_obj=None):
    mock_dfu = create_autospec(DataFileUtil, instance=True)

    ##
    ## mock `save_objects`
    def mock_dfu_save_objects(params):
        logging.info('Mocking dfu.save_objects(%s)' % str(params)[:200] + '...' if len(str(params)) > 200 else params)

        return [['mock', 1, 2, 3, 'dfu', 5, 'save_objects']] # UPA made from pos 6/0/4

    ##
    ## mock `get_objects`
    def mock_dfu_get_objects(params):
        logging.info('Mocking dfu.get_objects(%s)' % params)

        upa = ref_leaf(params['object_refs'][0])
        fp = _glob_upa(GET_OBJECTS_DIR, upa)

        # Download and cache
        if fp is None:
            logging.info('Calling in cache mode `dfu.get_objects`')

            dfu = DataFileUtil(os.environ['SDK_CALLBACK_URL'])
            obj = dfu.get_objects(params)
            fp = os.path.join(
                mkcache(GET_OBJECTS_DIR),
                file_safe_ref(upa) + '__' + obj['data'][0]['info'][1] + '.json'
            )
            with open(fp, 'w') as fh: json.dump(obj, fh)

        # Pull from cache
        else:
            with open(fp) as fh:
                obj = json.load(fh)

        # swap in arg obj
        if replace_obj is not None:
            ref = params['object_refs'][0]
            if ref in replace_obj:
                obj['data'][0]['data'] = replace_obj[ref]

        return obj

    mock_dfu.save_objects.side_effect = mock_dfu_save_objects
    mock_dfu.get_objects.side_effect = mock_dfu_get_objects

    return mock_dfu

mock_dfu = get_mock_dfu()


## MOCK RUN_CHECK ##

'''
def get_mock_run_check(dataset):
    mock_run_check = create_autospec(run_check)

    # side effect
    def mock_run_check_(cmd):
        logging.info('Mocking running cmd `%s`' % cmd)

        # test data
        src_drpth = os.path.join(TEST_DATA_DIR, 'return', dataset, 'return/output')

        # check if it already exists
        # since app may create it before run, and
        # since `check_run` is called twice in this app
        if os.path.exists(Var.out_dir):
            rmtree(Var.out_dir)
        copytree(src_drpth, Var.out_dir)


    mock_run_check.side_effect = mock_run_check_

    return mock_run_check
'''

## MOCK KBR ##

def mock_create_extended_report(params):
    logging.info('Mocking `kbr.create_extended_report`')

    return {
        'name': 'kbr_mock_name',
        'ref': 'kbr/mock/ref',
    }

mock_kbr = create_autospec(KBaseReport, instance=True, spec_set=True) 
mock_kbr.create_extended_report.side_effect = mock_create_extended_report


## UTIL ##

def mkcache(dir):
    dir = dir.replace(TEST_DATA_DIR, CACHE_DIR)
    os.makedirs(dir, exist_ok=True)
    return dir

def _glob_upa(data_dir, upa):
    p_l = list(Path(data_dir).glob(file_safe_ref(upa) + '*'))
    if len(p_l) == 0:
        return None
    elif len(p_l) > 1:
        raise Exception(upa)

    src_p = str(p_l[0])

    return src_p

def _house_mock_in_work_dir(src_p, dst_n=None):
    src_n = os.path.basename(src_p)

    house_dir = os.path.join(WORK_DIR, 'mock_house_' + str(uuid.uuid4()))
    os.mkdir(house_dir)

    dst_p = os.path.join(house_dir, dst_n if dst_n is not None else src_n)

    if Path(src_p).is_file():
        shutil.copyfile(src_p, dst_p)
    elif Path(src_p).is_dir():
        shutil.copytree(src_p, dst_p)

    return dst_p


def ref_leaf(ref):
    return ref.split(';')[-1]

def file_safe_ref(ref):
    return ref.replace('/', '.').replace(';', '_')

TRANSFORM_NAME_SEP = '_'



