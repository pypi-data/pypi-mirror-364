'''
Script holding ConstraintReader class
'''
from dmu.logging.log_store       import LogStore
from rx_efficiencies.decay_names import DecayNames as dn
from fitter.prec_scales          import PrecScales

log=LogStore.add_logger('fitter:constraint_reader')
# -------------------------------------------------------------
class ConstraintReader:
    '''
    Class meant to provide constraints for fitting model
    '''
    # -------------------------------------------------------------
    def __init__(self, parameters : list[str], q2bin : str):
        '''
        Parameters: List of parameter names as in the PDF
        q2bin     : q2 bin
        '''

        self._l_par   = parameters
        self._q2bin   = q2bin

        self._d_const = {}
        self._signal  = 'bpkpee' # This is the signal decay nickname, needed for PRec scales constraints
        self._prc_pref= 'pscale' # This is the partially reconstructed scale preffix.
                                 # Yields are of the form: pscale{SAMPLENAME}
                                 # pscale needs to be removed to access sample name
    # -------------------------------------------------------------
    def _add_signal_constraints(self) -> None:
        raise NotImplementedError('This needs to be implemented with DataFitter')
    # -------------------------------------------------------------
    def _proc_from_par(self, par_name : str) -> str:
        sample = par_name.lstrip(self._prc_pref)
        decay  = dn.nic_from_sample(sample)

        return decay
    # -------------------------------------------------------------
    def _add_prec_constraints(self) -> None:
        for par in self._l_par:
            if not par.startswith('pscale'): # PRec constraints are scales, starting with "s"
                continue

            log.debug(f'Adding constrint for: {par}')

            process  = self._proc_from_par(par)
            obj      = PrecScales(proc=process, q2bin=self._q2bin)
            val, err = obj.get_scale(signal=self._signal)

            self._d_const[par] = val, err
    # -------------------------------------------------------------
    def get_constraints(self) -> dict[str,tuple[float,float]]:
        '''
        Returns dictionary with constraints, i.e.

        Key  : Name of fitting parameter
        Value: Tuple with mu and error
        '''
        self._add_prec_constraints()

        return self._d_const
# -------------------------------------------------------------
