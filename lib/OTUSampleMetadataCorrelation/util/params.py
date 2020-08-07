import json

from .config import Var
from .dprint import dprint


DEFAULTS = dict(
    abund_cutoff=None,
    sd_cutoff=None,
    freq_cutoff=None,
    cor_cutoff=0.5,
    cor_method='kendall',
    p_adj_method='BH',
    p_adj_cutoff=0.05,
)

TYPES = dict(
    abund_cutoff=float,
    sd_cutoff=float,
    freq_cutoff=float,
    cor_cutoff=float,
    cor_method=str,
    p_adj_method=str,
    p_adj_cutoff=float,
)

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

        ## TODO validation

        ## ungroup
        params = flatten(params)
        

        ## custom transformations to internal representation ##
        if params.get("tax_rank") == 'None':
            params['tax_rank'] = None

        self.params = params


    def cmd_params_l(self) -> list:
        
        l = []

        for k in DEFAULTS.keys():
            if self.params[k] != DEFAULTS[k]:
                s = k + '='
                s += str(self.params[k]) if TYPES[k] is float else "'%s'" % self.params[k]
                l += [s]
             
        dprint('self.params', "', '.join(l)", run=locals())

        return l



    def get(self, key):
        return self.params.get(key)

        
    def __contains__(self, key):
        return key in self.params

    def __getitem__(self, key):
        return self.params[key]


    def __repr__(self):
        return 'Wrapper for params\n%s' % (json.dumps(self.params, indent=4))


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


