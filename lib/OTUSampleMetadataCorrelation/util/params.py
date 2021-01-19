import json

from .config import Var
from .dprint import dprint


VALID_PARAMS = [
#-------------------------------- required
    'amp_mat_upa',
    'sample_metadata',
    'workspace_id',
    'workspace_name',
#-------------------------------- param groups
    'amp_params',
    'cor_params',
#-------------------------------- default-backed
    'val_cutoff',
    'sd_cutoff',
    'tax_rank',
    'tax_field',
    'cor_cutoff',
    'cor_method',
    'p_adj_method',
    'p_adj_cutoff',
]

DEFAULTS = dict(
    val_cutoff=None,
    sd_cutoff=None,
    #freq_cutoff=None,
    tax_rank=None,
    tax_field=None,
    cor_cutoff=0.5,
    cor_method='kendall',
    p_adj_method='BH',
    p_adj_cutoff=0.05,
)


NON_DEFAULTS = [
    'amp_mat_upa',
    'sample_metadata',
    'workspace_id',
    'workspace_name'
]

DEFAULTS_TO_NOT_PASS = [ # default-backed params, but not passing to Rmd as arg
   'tax_field',
]

TYPES = dict(
    val_cutoff=float,
    sd_cutoff=float,
    #freq_cutoff=float,
    tax_rank=str,
    tax_field=str,
    cor_cutoff=float,
    cor_method=str,
    p_adj_method=str,
    p_adj_cutoff=float,
)

NULL_VALS = ['None', '', None]

class Params:
    '''
    Class adapting the narrative UI to the internal representation of the params
    (flat and with null cases),
    then to other representations of those params, e.g.,
    CLI args and human-readable

    For simplicity, all paramaters are required, but some are "optional"
    in the sense that they can be None
    '''

    def __init__(self, params):

        self._validate(params)

        # ungroup 
        params = self.flatten(params)
        

        ###
        ### Custom transformations to internal representation

        # rep this as list for now
        # thought we'd do multiple sample metadata fields one day
        if not isinstance(params['sample_metadata'], list):
            params['sample_metadata'] = [params['sample_metadata']]

        if params.get('tax_rank') in NULL_VALS:
            params['tax_rank'] = None
        if params['tax_field'] in NULL_VALS:
            params['tax_field'] = None

        # if either tax_rank or tax_field are None,
        # the other is conceptually None
        if params.get('tax_rank') is None:
            params['tax_field'] = None
        if params.get('tax_field') is None:
            params['tax_rank'] = None

        # required single fields are passed as string,
        # but optional single fields are passed as list of string
        if type(params.get('tax_field')) is list:
            params['tax_field'] = params.get('tax_field')[0]


        self._validate(params)

        self.params = params


    def _validate(self, params):
        # make sure nothing misspelled passed in
        for p in params:
            if p not in VALID_PARAMS:
                raise Exception(p)

        


    def cmd_params_l(self) -> list:
        
        l = []

        for k in DEFAULTS.keys():
            if k in DEFAULTS_TO_NOT_PASS:
                continue # some default-backed, like tax_field, aren't passed to Rmd
            if self.getd(k) != DEFAULTS[k]:
                s = k + '='
                s += str(self.params[k]) if TYPES[k] is float else "'%s'" % self.params[k]
                l += [s]
             
        dprint('self.params', "', '.join(l)", run=locals())

        return l

        
    def __contains__(self, key):
        return key in self.params


    def getd(self, key):
        '''
        Use this for default-backed params
        '''
        if key not in DEFAULTS:
            raise Exception("Key `%s` not default-backed, so can't use params.getd()" % key)
        return self.params.get(key, DEFAULTS[key])



    def __getitem__(self, key):
        '''
        Use this for required params
        '''
        if key in DEFAULTS:
            raise Exception("Key `%s` is default-backed, thus optional, so you should use params.getd()" % key)
        return self.params[key]


    def __repr__(self):
        return 'Wrapper for params\n%s' % (json.dumps(self.params, indent=4))


    @staticmethod
    def flatten(d):
        '''
        Handles at most 1 level nesting
        '''
        d1 = d.copy()
        for k, v in d.items():
            if isinstance(v, dict):
                for k1, v1 in d1.pop(k).items():
                    d1[k1] = v1
        return d1


