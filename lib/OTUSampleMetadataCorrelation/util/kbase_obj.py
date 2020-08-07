import logging
import pandas as pd
import numpy as np
import os
import sys
import json

from .config import Var
from .dprint import dprint


def write_json(obj, flnm, AmpliconSet=False):
    '''
    For debugging/testing
    '''
    if 'run_dir' not in Var:
        import uuid
        Var.run_dir = os.path.join('/kb/module/work/tmp', str(uuid.uuid4()))
        os.mkdir(Var.run_dir)

    flpth = os.path.join(Var.run_dir, flnm)
    with open(flpth, 'w') as f:
        json.dump(obj, f)

    if AmpliconSet == True:
        dprint('touch %s' % os.path.join(Var.run_dir, '#' + obj['data'][0]['info'][1]), run='cli') # annotate run_dir with name



####################################################################################################
####################################################################################################
class AmpliconMatrix:

    def __init__(self, upa):
        '''
        Instance variables created during init:
        * upa
        * name
        * obj
        '''
        self.upa = upa
        self._get_obj()


    def _get_obj(self):
        logging.info('Loading object info for AmpliconMatrix `%s`' % self.upa)

        obj = Var.dfu.get_objects({
            'object_refs': [self.upa]
        })

        if Var.debug: write_json(obj, 'get_objects_AmpliconMatrix.json')

        self.name = obj['data'][0]['info'][1]
        self.obj = obj['data'][0]['data']


    def to_otu_table(self, flpth):
        '''
        Pass `None` to not write (for testing)

        `id` is first column
        '''

        logging.info("Writing OTU table from AmpliconMatrix")

        data = np.array(self.obj['data']['values'], dtype=float)
        row_ids = self.obj['data']['row_ids']
        col_ids = self.obj['data']['col_ids']

        df = pd.DataFrame(
            data, 
            index=row_ids, 
            columns=col_ids
        )

        
        df.to_csv(flpth, sep='\t')

        return df # for testing




####################################################################################################
####################################################################################################
class AttributeMapping:

    def __init__(self, upa):
        '''
        Instance variables created at init time:
        * upa
        * name
        * obj
        '''
        self.upa = upa
        self._get_obj()


    def _get_obj(self):
        logging.info('Loading object info for AttributeMapping `%s`' % self.upa)

        obj = Var.dfu.get_objects({
            'object_refs': [self.upa]
        })

        if Var.debug: write_json(obj, 'get_objects_AttributeMapping.json')

        self.name = obj['data'][0]['info'][1]
        self.obj = obj['data'][0]['data']


    def to_metadata_table(self, flpth):

        attributes = self.obj['attributes']
        instances = self.obj['instances']

        df = pd.DataFrame.from_dict(instances, orient='index')
        df.columns = [attribute['attribute'] for attribute in attributes]
        
        df.to_csv(flpth, sep='\t')

        return df # for testing


   
    def attribute_index_1based(self, attrName):

        for ind, attribute_d in enumerate(self.obj['attributes']):
            if attrName == attribute_d['attribute']:
                return ind + 1

        raise Exception()

