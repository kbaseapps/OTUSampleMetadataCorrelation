import logging
import pandas as pd
import numpy as np
import os
import sys
import json

from .config import Var
from .dprint import dprint
from .error import * # exceptions


####################################################################################################
####################################################################################################
def replace_missing(df, replacement=np.nan):
    MISSING_VALS = ['', 'nan', 'None', 'null', np.nan] # None troublesome using `df.replace`
    
    for missing in MISSING_VALS:
        try:
            df = df.replace(missing, replacement)
        except:
            raise Exception('`%s` vs `%s`' %(missing,replacement))

    return df

####################################################################################################
####################################################################################################
def is_missingAdj_numeric(df: pd.DataFrame):
    df = replace_missing(df)

    try:
        df.astype('float')
        return True
    except ValueError:
        return False

    raise

####################################################################################################
####################################################################################################
def as_missingAdj_numeric(df: pd.DataFrame, replacement=np.nan):
    df = replace_missing(df, replacement)

    try:
        return df.astype('float')
    except ValueError:
        return None

    raise

####################################################################################################
####################################################################################################
def num_nan_in_missingAdj_numeric(df: pd.DataFrame):
    '''
    Only works on numeric types
    '''

    df = as_missingAdj_numeric(df, replacement=np.nan)

    return np.isnan(df.values).sum().sum()

####################################################################################################
####################################################################################################
def num_emptyStr_in_missingAdj_obj(df: pd.DataFrame):
    df = replace_missing(df, replacement='')
    return (df=='').sum().sum()

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


    def check_data_valid(self):
        df = self.to_otu_table(flpth=None)

        if not is_missingAdj_numeric(df):
            raise DataException('AmpliconMatrix data must be numeric')
        elif num_nan_in_missingAdj_numeric(df) > 0:
            raise DataException('Currently not supporting missing values in AmpliconMatrix')



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
    def as_canonical(self, tax_str: str):
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
    def looks_canonical(self, tax_str: str):
        # tokenize
        toks = [tok.strip() for tok in tax_str.split(';')]

        # 7 semicolons (8 slots) only okay if ends in semicolon
        if len(toks) == self.NSLOTS + 1:
            if toks[-1] != '':
                return False
        # otherwise more than 6 semicolons (7 slots) not okay 
        elif len(toks) > self.NSLOTS:
            return False

        return True


    #####
    #####
    def to_tax_table(self, flpth=None):
        self.check(1)

        id2tax = self.get_id2tax()

        # Warn about any non-canonical tax
        for tax_str in id2tax.values():
            if not self.looks_canonical(tax_str):
                msg = (
                    'Detecting taxonomy string `%s` that does not look canonical. '
                    'See app documentation for more info'
                    % tax_str
                )
                logging.warning(msg)
                Var.warnings.append(msg)
                break

        id2tax = {
            id: self.as_canonical(tax_str) 
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
    def check_tax_data_valid(self):
        self.check(1)

        df = self.to_tax_table(flpth=None)

        if num_emptyStr_in_missingAdj_obj(df) == df.size:
            raise DataException(
                'Sorry, taxonomy table, '
                'when parsed from row AttributeMapping %s with field %s, '
                'is empty'
                % (self.name, Var.params.getd('tax_field'))
            )

    #####
    #####
    def get_id2tax(self):
        '''
        Use AmpMat ids (so use reverse amp_mat.row_mapping)
        '''
        self.check(1)

        # find ind
        ind = -1 # empty attributes case
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
        
        return id2tax


######################################################################## COLUMN ####################
    #####
    #####
    def to_metadata_table(self, flpth=None):
        '''
        For column AttributeMapping
        '''
        self.check(2)

        attributes = self.obj['attributes']
        instances = self.obj['instances']

        df = pd.DataFrame.from_dict(instances, orient='index')#; dprint('df', run=locals())
        df = replace_missing(df, '')#; dprint('df', run=locals())
        df.columns = [attribute['attribute'] for attribute in attributes]#; dprint('df', run=locals())
        
        if flpth is not None:
            df.to_csv(flpth, sep='\t')

        return df # for testing


   
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

    #####
    #####
    def check_sample_metadata_valid(self):
        '''
        Has a minimum number of non-missing values
        Is otherwise numerical
        '''
        self.check(2)

        MIN_NOT_MISSING = 5 # also in app documentation

        m = self.to_metadata_table()
        m = m[[Var.params['sample_metadata'][0]]] # df with selected sample metadata

        if not is_missingAdj_numeric(m):
            msg = (
                "Sorry, please choose sample metadata that is numeric. "
                "(Integers, floats, and missing.)"
            )
            raise DataException(msg)

        if m.values.size - num_nan_in_missingAdj_numeric(m) < MIN_NOT_MISSING:
            msg = (
                "Sorry, please choose sample metadata that has a minimum of %d, non-missing values"
                % MIN_NOT_MISSING
            )
            raise DataException(msg)


