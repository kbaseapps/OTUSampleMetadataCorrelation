import numpy as np

from .dprint import dprint



####################################################################################################
####################################################################################################
MISSING_VALS = [None, '', 'None', np.nan] # Below functions should implicitly handle these missing values
                                        # This pertains to all numpy arrays handled here, whether straight from JSON or intermediary

class Validate:
    '''
    Use np.ndarray because
    (1) Easier to detect `None`
    (2) Common denominator
    '''
####################################################################################################
####################################################################################################
    @classmethod
    def replace_missing(cls, a: np.ndarray, rep=np.nan):
        '''
        '''    
        if np.issubdtype(a.dtype, int) and rep in [np.nan, None]:
            raise Exception('Cannot assign special missing values to numpy integer array')

        for missing in MISSING_VALS:
            try:
                a[a == np.array(missing, dtype=object)] = rep
            except:
                raise Exception(missing)

        return a

####################################################################################################
####################################################################################################
    @classmethod
    def get_num_missing(cls, a: np.ndarray):
        num = 0
        for missing in MISSING_VALS:
            num = num + (a == np.array(missing, dtype=object)).sum() # cast missing as obj np.array to get element-wise comparison
        
        return num


####################################################################################################
####################################################################################################
    @classmethod
    def as_numeric(cls, a: np.ndarray, rep=np.nan, dtype=float):
        '''
        Cast to numeric, taking care of missing values

        Warning: NumPy integer arrays do not support missing values (np.nan etc.)
        Also a.astype(int) will truncate floats into ints
        '''

        if np.issubdtype(dtype, int) and rep in [np.nan, None]:
            raise Exception('Cannot assign special missing values to numpy integer array')

        if np.issubdtype(a.dtype, int) and rep in [np.nan, None]:
            a = a.astype(float) # cast to float first to allow assigning special values

        a = cls.replace_missing(a)

        try:
            a = a.astype(dtype)
            return a
        except ValueError:
            return None

        raise


####################################################################################################
####################################################################################################
    @classmethod
    def is_numeric(cls, a: np.ndarray):
        if cls.as_numeric(a) is not None:
            return True
        else:
            return False



####################################################################################################
####################################################################################################
    @classmethod
    def is_int_like(cls, a: np.ndarray, missingOk=True):
        '''
        '''

        allclose_ = functools.partial(
            np.allclose, 
            equal_nan=missingOk, # NaNs equal 
            atol=1e-8, # same
            rtol=1e-8, # decrease otherwise 4.00001 == 4
        )
        a_round = np.round(a)

        return allclose_(a, a_round) and allclose_(a_round, a)
