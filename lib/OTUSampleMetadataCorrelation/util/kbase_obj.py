import logging
import pandas as pd
import numpy as np
import os
import sys
import json

from .config import Var
from .dprint import dprint
from .error import * # exceptions
from .validate import Validate as vd


####################################################################################################
####################################################################################################
####################################################################################################
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

        self.name = obj['data'][0]['info'][1]
        self.obj = obj['data'][0]['data']


    def to_otu_table(self, flpth=None):
        '''
        Call validation method first
        Pass `None` to not write (for testing)
        `id` is first column
        '''

        logging.info("Writing amplicon matrix to %s" % (flpth if flpth is not None else 'nowhere'))

        data = np.array(self.obj['data']['values'], dtype=float)
        row_ids = self.obj['data']['row_ids']
        col_ids = self.obj['data']['col_ids']

        df = pd.DataFrame(
            data, 
            index=row_ids, 
            columns=col_ids
        )
        df.index.name = 'id'

        if flpth is not None:
            df.to_csv(flpth, sep='\t')

        return df # for testing


    def check_data_valid(self): # TODO test
        df = np.array(self.obj['data']['values'], dtype=object)

        if vd.get_num_missing(df) > 0:
            raise ValidationException('Currently not supporting missing values in AmpliconMatrix')


    def rev_mapping(self, axis):
        '''
        Use col_mapping or row_mapping
        But in reverse, from AttrMap to AmpMat
        '''
        if axis in ['row', 1]:
            return {ida: idm for idm, ida in self.obj['row_mapping'].items()}
        elif axis in ['col', 2]:
            return {ida: idm for idm, ida in self.obj['col_mapping'].items()}

        raise Exception(axis)



####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################
class AttributeMapping:

    #####
    #####
    def __init__(self, upa, amp_mat, dim):
        '''
        Input parameters
        ----------------
        :upa:
        :amp_mat: for ref root and row_mapping/col_mapping
        :dim: 1 or 2, for row or column

        Instance variables created at init time:
        * upa
        * dim
        * name
        * obj
        '''
        self.upa = upa
        self.amp_mat = amp_mat
        self.dim = dim
        self._get_obj()


    #####
    #####
    def _get_obj(self):
        logging.info('Loading object info for AttributeMapping `%s`' % self.upa)

        obj = Var.dfu.get_objects({
            'object_refs': ['%s;%s' % (self.amp_mat.upa, self.upa)]
        })

        self.name = obj['data'][0]['info'][1]
        self.obj = obj['data'][0]['data']

    #####
    #####
    def check(self, dim):
        '''
        This class supports both row and column AttributeMappings
        This is to try to keep them from being mixed up
        '''
        if dim != self.dim:
            raise Exception()

############################################################################ ROW ###################
    
    NSLOTS = 7 # canonical num slots for taxonomy (domain thru species)

    #####
    #####
    def _as_canonical_l(self, tax_str: str):
        '''
        Pad or reduce taxa list to 7 slots
        '''
        tax_l = [t.strip() for t in tax_str.split(';')]
        length = len(tax_l)
        if length == self.NSLOTS:
            return tax_l
        elif length < self.NSLOTS:
            return tax_l + [''] * (self.NSLOTS-length)
        elif length > self.NSLOTS:
            return tax_l[:self.NSLOTS]


    #####
    #####
    def to_tax_table(self, flpth=None):
        self.check(1)

        id2tax = self.get_id2tax() # id to str

        id2tax = {
            id: self._as_canonical_l(tax_str) 
            for id, tax_str in id2tax.items()
        } # id to 7-slot taxa list
 
        df = pd.DataFrame.from_dict(id2tax, orient='index')
        df.columns = ['domain', 'phylum', 'class', 'order', 'family', 'genus', 'species']
        df.index.name = 'id'

        if flpth is not None:
            df.to_csv(flpth, sep='\t')

        return df # for testing, validation


    #####
    #####
    def check_tax_data_valid(self): # TODO test
        self.check(1)

        a = self.to_tax_table(flpth=None).values

        if vd.get_num_missing(a) == a.size:
            raise ValidationException(
                'Sorry, taxonomy table, '
                'when parsed from row AttributeMapping %s with field %s, '
                'is empty'
                % (self.name, Var.params.getd('tax_field'))
            )

    #####
    #####
    def get_id2tax(self):
        '''
        Use AmpMat ids rather than row AttrMap ids
        (so use reverse amp_mat.row_mapping)

        Replace `null` tax strs with `''`
        '''
        self.check(1)

        # find ind
        ind = -1 # no attribute case
        for i, attribute in enumerate(self.obj['attributes']):
            if attribute['attribute'] == Var.params.getd('tax_field'):
                ind = i
                break

        if ind == -1:
            msg = (
                "Sorry, the input row AttributeMapping `%s` has no attribute `%s`. "
                % (self.name, Var.params.getd('tax_field'))
            )
            raise NoTaxonomyException(msg )

        # get mapping
        # from AmpliconMatrix ids
        rev_row_mapping = self.amp_mat.rev_mapping(axis='row')
        id2tax = {rev_row_mapping[id]: instance[ind] for id, instance in self.obj['instances'].items()}

        # replace `null` tax strs with `''`
        id2tax = {id: ('' if tax is None else tax) for id, tax in id2tax.items()}
        
        return id2tax


######################################################################## COLUMN ####################

    #####
    #####
    def to_metadata_table(self, flpth=None):
        '''
        For column AttributeMapping

        For now: write the whole table. 
        Theoretically the Rmd can be modified to do multiple sample metadata
        '''
        self.check(2)

        attributes = self.obj['attributes']
        instances = self.obj['instances']

        df = pd.DataFrame.from_dict(instances, orient='index')#; dprint('df', run=locals())
        df = pd.DataFrame(
            data=vd.replace_missing(df.values, ''), 
            index=df.index, 
            columns=[attribute['attribute'] for attribute in attributes]
        )#; dprint('df', run=locals())
        
        if flpth is not None:
            df.to_csv(flpth, sep='\t')

        return df # for testing


    #####
    #####
    def check_sample_metadata_valid(self): #TODO validate
        '''
        Has a minimum number of non-missing values
        Is otherwise numerical
        '''
        self.check(2)

        MIN_NOT_MISSING = 5 # also in app documentation

        df = self.to_metadata_table()
        df = df[[Var.params['sample_metadata'][0]]] # df with selected sample metadata
        a = df.values

        if not vd.is_numeric(a):
            msg = (
                "Sorry, please choose sample metadata that is numeric. "
                "(Integers, floats, and missing.)"
            )
            raise ValidationException(msg)

        if a.size - vd.get_num_missing(a) < MIN_NOT_MISSING:
            msg = (
                "Sorry, please choose sample metadata that has a minimum of %d, non-missing values"
                % MIN_NOT_MISSING
            )
            raise ValidationException(msg)

   
    #####
    #####
    def attribute_index_1based(self, attrName): # TODO match AmpMat col ordering
        '''
        For column AttributeMapping
        '''
        self.check(2)

        for ind, attribute_d in enumerate(self.obj['attributes']):
            if attrName == attribute_d['attribute']:
                return ind + 1

        raise Exception('`%s`' % attrName)


