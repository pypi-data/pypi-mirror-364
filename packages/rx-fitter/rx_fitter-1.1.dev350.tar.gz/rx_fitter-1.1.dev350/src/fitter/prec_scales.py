'''
Module containing class ModelScales and helper functions
'''

import math
import numpy
import pandas   as pnd
import jacobi   as jac

from dmu.logging.log_store                 import LogStore
from dmu.generic                           import hashing
from dmu.generic                           import utilities  as gut
from rx_selection                          import selection  as sel
from rx_efficiencies.decay_names           import DecayNames as dn
from rx_efficiencies.efficiency_calculator import EfficiencyCalculator

log=LogStore.add_logger('fitter:prec_scales')
#------------------------------------------
class PrecScales:
    '''
    Class used to calculate scale factor between yields of partially reconstructed component and signal
    '''
    #------------------------------------------
    def __init__(self, proc : str, q2bin : str):
        '''
        proc : Nickname of decay process, nicknames are in the DecayNames class
        q2bin: Needed to apply correct selection to get correct efficiencies and scales
        '''
        self._proc        = proc
        self._q2bin       = q2bin

        self._d_frbf      : dict
        self._trigger     = 'Hlt2RD_BuToKpEE_MVA'
        self._initialized = False

        self._hash        = self._get_hash()
    #------------------------------------------
    def _get_hash(self) -> str:
        process = dn.sample_from_decay(self._proc)
        d_sel   = sel.selection(trigger=self._trigger, q2bin=self._q2bin, process=process)
        hsh     = hashing.hash_object([self._proc, self._q2bin, d_sel])

        return hsh
    #------------------------------------------
    def _check_arg(self, l_val, val, name):
        if val not in l_val:
            raise ValueError(f'{name} {val} not allowed')

        log.debug(f'{name:<20}{"->":20}{val:<20}')
    #------------------------------------------
    def _initialize(self):
        if self._initialized:
            return

        log.debug('Initializing')
        self._d_frbf = gut.load_data(package='rx_efficiencies_data', fpath='scales/fr_bf.yaml')

        self._initialized = True
    #------------------------------------------
    def _get_fr(self, proc : str) -> float:
        '''
        Returns hadronization fraction for given process
        '''
        if   proc.startswith('bp'):
            fx = 'fu'
        elif proc.startswith('bd'):
            fx = 'fd'
        elif proc.startswith('bs'):
            fx = 'fs'
        else:
            raise ValueError(f'Cannot find hadronization fraction for: {proc}')

        fx = self._d_frbf['fr'][fx]

        return fx
    #------------------------------------------
    def _mult_brs(self, l_br : list[tuple[float,float]]) -> tuple[float,float]:
        '''
        Parameters
        -----------------------
        l_br: List of branching fraction, branching fraction error tuples

        Returns
        -----------------------
        A tuple with the product of those branching fractions and the error in the product
        '''
        log.debug('Multiplying branching fractions')

        l_br_val = [ float(br[0]) for br in l_br ] # These numbers come from YAML files
        l_br_err = [ float(br[1]) for br in l_br ] # when using "e" in scientific notation, these numbers are made into strings

        br_cov   = numpy.diag(l_br_err) ** 2
        val, var = jac.propagate(
            math.prod,
            l_br_val,
            br_cov)

        err      = math.sqrt(var)
        val      = float(val)

        return val, err
    #------------------------------------------
    def _get_br(self, proc : str) -> tuple[float,float]:
        log.debug(f'Calculating BR for {proc}')

        l_dec = dn.subdecays_from_nickname(proc)
        l_bf  = [ self._d_frbf['bf'][dec] for dec in l_dec ]

        return self._mult_brs(l_bf)
    #------------------------------------------
    def _get_ef(self, proc : str) -> tuple[float,float]:
        '''
        Parameters
        --------------
        proc: Nickname to process, e.g. bpkpee

        Returns
        --------------
        Tuple with efficiency value and error
        '''
        sample = dn.sample_from_decay(proc)

        log.debug(f'Calculating efficiencies for {sample}')
        obj = EfficiencyCalculator(q2bin=self._q2bin)
        val = obj.get_efficiency(sample=sample)

        return val
    #------------------------------------------
    def _print_vars(self, l_tup : list[tuple[float,float]], proc : str) -> None:
        log.debug('')
        log.debug(f'Decay: {proc}')
        log.debug('-' * 20)
        log.debug(f'{"Var":<20}{"Value":<20}{"Error":<20}')
        log.debug('-' * 20)
        for (val, err), name in zip(l_tup, ['fr', 'br', 'eff']):
            log.debug(f'{name:<20}{val:<20.3e}{err:<20.3e}')
        log.debug('-' * 20)
    #------------------------------------------
    def get_scale(self, signal : str) -> tuple[float,float]:
        '''
        Parameters
        -----------------------
        signal: String representing signal WRT which to scale, e.g. bpkpee

        Returns
        ---------------
        Scale factor k and error, meant to be used in:

        Nprec = k * Nsignal

        reparametrization, during fit.
        '''
        self._initialize()

        fr_bkg = self._get_fr(self._proc)
        br_bkg = self._get_br(self._proc)
        ef_bkg = self._get_ef(self._proc)

        fr_sig = self._get_fr(signal)
        br_sig = self._get_br(signal)
        ef_sig = self._get_ef(signal)

        l_tup = [fr_sig, br_sig, ef_sig, fr_bkg, br_bkg, ef_bkg]
        l_val = [ tup[0] for tup in l_tup]
        l_err = [ tup[1] for tup in l_tup]
        cov   = numpy.diag(l_err) ** 2

        self._print_vars(l_tup[:3], proc=    signal)
        self._print_vars(l_tup[3:], proc=self._proc)

        val, var = jac.propagate(lambda x : (x[3] * x[4] * x[5]) / (x[0] * x[1] * x[2]), l_val, cov)
        val = float(val)
        err = math.sqrt(var)

        return val, err
#------------------------------------------
