'''
This module contains BaseFitter
'''
from typing                   import cast
import matplotlib.pyplot as plt

from omegaconf                import OmegaConf, DictConfig
from dmu.stats.fitter         import Fitter
from dmu.stats.zfit_plotter   import ZFitPlotter
from dmu.generic              import utilities  as gut
from dmu.stats                import utilities  as sut
from dmu.logging.log_store    import LogStore
from rx_selection             import selection  as sel
from zfit.result              import FitResult  as zres
from zfit.core.interfaces     import ZfitData   as zdata
from zfit.core.interfaces     import ZfitPDF    as zpdf

log=LogStore.add_logger('fitter:base_fitter')
# ------------------------
class BaseFitter:
    '''
    Fitting base class, meant to

    - Provide basic functionality to fiters for data and simulation
    - Behave as a dependency sink, avoiding circular imports
    '''
    # ------------------------
    def __init__(self):
        '''
        Used to hold attributes passed from derived classes
        '''
        self._sample  : str = ''
        self._trigger : str = ''
        self._project : str = ''
        self._q2bin   : str = ''
    # ------------------------
    def _fit(
            self,
            cfg   : DictConfig,
            data  : zdata,
            model : zpdf,
            d_cns : dict[str,tuple[float,float]]|None = None) -> zres:
        '''
        Parameters
        --------------------
        cfg  : Fitting configuration
        data : Zfit data object
        model: Zfit PDF
        d_cns: Dictionary mapping parameter names to tuples of value and error
               This is needed to apply constraints to fit

        Returns
        --------------------
        DictConfig object with parameters names, values and errors
        '''
        fit_cfg = OmegaConf.to_container(cfg, resolve=True)
        fit_cfg = cast(dict, fit_cfg)

        if d_cns is not None:
            fit_cfg['constraints'] = d_cns

        ftr = Fitter(pdf=model, data=data)
        res = ftr.fit(cfg=fit_cfg)

        return res
    # ------------------------
    def _get_sensitivity(self, res : zres|None) -> float:
        '''
        Parameters
        --------------
        res: Result object from fit

        Returns
        --------------
        fit sensitivity in %
        '''
        if res is None:
            log.debug('Missing result object, cannot get sensitivity')
            return -1

        cres = sut.zres_to_cres(res=res)

        if 'nsignal' not in cres:
            log.debug('Missing nsig entry, cannot get sensitivity')
            return -1

        value = cres['nsignal']['value']
        error = cres['nsignal']['error']

        return 100 * error / value
    # --------------------------
    def _brem_cuts_from_cuts(self, cuts : dict[str,str]) -> str:
        '''
        Parameters
        --------------
        cuts: Dictionary with cuts used for fit

        Returns
        --------------
        String with brem requirements
        '''
        l_brem_cut = []
        for cut in cuts.values():
            if 'nbrem' not in cut:
                continue
            l_brem_cut.append(cut)

        brem_cuts = '; '.join(l_brem_cut)

        return brem_cuts
    # --------------------------
    def _get_selection_text(self, cuts : dict[str,str]) -> tuple[str,str]:
        '''
        Parameters
        --------------
        cuts: Dictionary with cuts used for fit

        Returns
        --------------
        Tuple with:

        - Multiple lines with cuts that were used for fit, but are not default, plus MVA cut
        - Brem categories choice
        '''
        # For components like combinatorial, there is no MC sample
        # Therefore the selection or brem category does not make sense
        if self._sample == 'NA':
            return '', ''

        brem_cuts = self._brem_cuts_from_cuts(cuts=cuts)
        # Pick default selection
        with sel.custom_selection(d_sel={}):
            d_sel_def = sel.selection(
                process=self._sample,
                trigger=self._trigger,
                q2bin  =self._q2bin)

        l_expr = []
        # Collect all the cuts that are different
        # from default selection
        for name, expr in cuts.items():
            if name not in d_sel_def:
                expr = cuts[name]
                l_expr.append(expr)
                continue

            def_expr = d_sel_def[name]
            if expr != def_expr:
                l_expr.append(expr)

        # Remove differences in brem, will be done separately
        l_expr_no_brem = [ expr for expr in l_expr if 'nbrem' not in expr ]
        new_cuts       = '\n'.join(l_expr_no_brem)

        return new_cuts, brem_cuts
    # --------------------------
    def _entries_from_data(self, data : zdata) -> int:
        '''
        Parameters
        ---------------
        data: Dataset used in the fit

        Returns
        ---------------
        Number of entries in data that were used for the fit,
        which are in the fit observable range
        '''
        obs          = data.space
        [minx, maxx] = sut.range_from_obs(obs=obs)

        arr_mass = data.to_numpy()
        mask     = (minx < arr_mass) & (arr_mass < maxx)
        arr_mass = arr_mass[mask]
        nentries = len(arr_mass)

        return nentries
    # --------------------------
    def _get_text(
            self,
            data : zdata,
            res  : zres|None,
            cuts : dict[str,str]) -> tuple[str,str]:
        '''
        Parameters
        --------------
        data: Zfit data used for fit
        res : zfit result object
        cuts: Dictionary with cuts used to get data

        Returns
        --------------
        Tuple with:

        - Title for fit plot
        - Text that goes inside plot with selection information
        '''
        nentries          = self._entries_from_data(data=data)
        sel_txt, brem_txt = self._get_selection_text(cuts=cuts)

        sensitivity = self._get_sensitivity(res=res)
        title       = f'$\\delta={sensitivity:.2f}$%; Entries={nentries:.0f}; Brem:{brem_txt}'

        return title, sel_txt
    # ------------------------
    def _save_fit(
            self,
            cuts     : dict[str,str],
            cfg      : DictConfig,
            out_path : str,
            model    : zpdf|None,
            res      : zres|None,
            data     : zdata,
            d_cns    : dict[str,tuple[float,float]]|None=None) -> None:
        '''
        Parameters
        --------------
        cuts     : Selection used for fit
        cfg      : Plotting configuration
        out_path : Directory where fit will be saved
        model    : PDF from fit, can be None if dataset was empty
        res      : Zfit result object, can be None if fit was to get a KDE
        data     : data from fit
        d_cns    : Dictionary mapping parameter name to value error tuple.
                   Used for constraining that parameter
        '''
        plt_cfg = OmegaConf.to_container(cfg, resolve=True)
        plt_cfg = cast(dict, plt_cfg)

        # If no entries were present
        # There will not be PDF
        title, text         = self._get_text(data=data, res=res, cuts=cuts)
        plt_cfg['title'   ] = title
        plt_cfg['ext_text'] = text

        if model is not None:
            ptr = ZFitPlotter(data=data, model=model)
            ptr.plot(**plt_cfg)
        else:
            plt.figure()

        sel_path = f'{out_path}/selection.yaml'
        gut.dump_json(cuts, sel_path)

        sut.save_fit(
            data   = data,
            model  = model,
            res    = res,
            d_const= d_cns,
            fit_dir= out_path)
# ------------------------
