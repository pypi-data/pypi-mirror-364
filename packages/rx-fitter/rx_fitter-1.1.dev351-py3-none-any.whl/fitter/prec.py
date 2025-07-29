'''
Module containing PRec
'''
import os
import copy
import json
import pprint
from typing     import Union
from contextlib import contextmanager

import numpy
import slugify
import pandas            as pnd
import matplotlib.pyplot as plt

from omegaconf              import OmegaConf
from dmu.stats.zfit         import zfit
from dmu.generic            import hashing
from dmu.logging.log_store  import LogStore
from dmu.stats.zfit_plotter import ZFitPlotter
from dmu.stats.utilities    import is_pdf_usable
from dmu.stats              import utilities as sut
from dmu.workflow.cache     import Cache

from zfit.core.parameter   import Parameter as zpar
from zfit.core.basepdf     import BasePDF   as zpdf
from zfit.core.interfaces  import ZfitSpace as zobs
from rx_selection          import selection as sel
from rx_data.rdf_getter    import RDFGetter
from ROOT                  import RDataFrame

from fitter.inclusive_decays_weights import Reader as inclusive_decays_weights
from fitter.inclusive_sample_weights import Reader as inclusive_sample_weights

log=LogStore.add_logger('fitter:prec')
#-----------------------------------------------------------
class PRec(Cache):
    '''
    Class used to calculate the PDF associated to the partially reconstructed background
    '''
    use_cache = True # Use cached if found
    #-----------------------------------------------------------
    def __init__(
        self,
        samples  : list[str],
        trig     : str,
        q2bin    : str,
        d_weight : dict[str,int],
        out_dir  : str = ''):
        '''
        Parameters:
        -------------------------
        samples  : MC samples
        trig     : HLT2 trigger.
        q2bin    : q2 bin
        d_weight : Dictionary specifying which weights to use, e.g. {'dec' : 1, 'sam' : 1}
        out_dir  : Directory where cached outputs will go WRT _cache_root, default empty
        '''
        self._l_sample = samples
        self._trig     = trig
        self._q2bin    = q2bin
        self._d_wg     = copy.deepcopy(d_weight)

        self._name     : str
        self._d_fstat  = {}
        d_rdf, uid     = self._get_samples_rdf()
        self._d_rdf    = d_rdf

        self._d_match         = self._get_match_str()
        self._l_mass          = ['B_Mass', 'B_Mass_smr', 'B_const_mass_M', 'B_const_mass_psi2S_M']
        self._min_entries     = 40 # Will not build KDE if fewer entries than this are found
        self._min_isj_entries = 500 #if Fewer entries than this, switch from ISJ to FFT

        self._check_valid(self._q2bin, ['low', 'central', 'jpsi', 'psi2', 'high'], 'q2bin')
        self._check_weights()

        # This should be usable to make hashes
        # backlashes and dollar signs are not hashable in strings
        d_hash_match = { slugify.slugify(ltex) : value for ltex, value in self._d_match.items() }

        super().__init__(
            out_path = out_dir,
            uid      = uid,
            d_wg     = OmegaConf.to_container(d_weight, resolve=True),
            d_match  = d_hash_match)
    #-----------------------------------------------------------
    def _get_df(self) -> dict[str,pnd.DataFrame]:
        '''
        Returns
        -------------------
        Dictionary where:

        Key  : Identifier for ccbar component, e.g. "$B_d\to c\bar{c}(\to ee)H_s$"
        Value: Dictionary with:
            Key  : Name of component
            Value: Dataframe with entries for only that component
        '''
        d_df = self._get_samples_df()
        d_df = { sample : self._add_dec_weights(sample, df) for sample, df in d_df.items() }
        df   = pnd.concat(d_df.values(), axis=0)
        df   = self._add_sam_weights(df)

        if len(df) == 0:
            return {}

        arr_wgt      = df.wgt_dec.to_numpy() * df.wgt_sam.to_numpy()
        df['wgt_br'] = self._normalize_weights(arr_wgt)

        d_df = { component : df.query(cut) for component, cut in self._d_match.items() }

        return d_df
    #-----------------------------------------------------------
    def _need_var(self, name : str) -> bool:
        needed = False

        if name.endswith('ID'):
            needed = True

        if name in self._l_mass:
            needed = True

        return needed
    #-----------------------------------------------------------
    def _filter_rdf(
        self,
        rdf    : RDataFrame,
        uid    : str,
        sample : str) -> tuple[RDataFrame,str]:
        '''
        Parameters
        -----------------
        rdf    : ROOT dataframe before selection
        uid    : Unique identifier of dataframe
        sample : Sample for which selection is done, e.g. Bu_JpsiX...

        Returns
        -----------------
        Tuple with:

        - ROOT dataframe after selection
        - Updated Unique identifier that takes into account the selection
        '''
        d_sel         = sel.selection(trigger=self._trig, q2bin=self._q2bin, process=sample)
        d_sel['mass'] = '(1)'
        for name, expr in d_sel.items():
            rdf = rdf.Filter(expr, name)

        uid = hashing.hash_object([uid, d_sel])

        return rdf, uid
    #-----------------------------------------------------------
    def _get_samples_rdf(self) -> tuple[dict[str,RDataFrame],str]:
        '''
        IMPORTANT: This method has to run dataframe creation lazily

        Returns
        -----------------
        Tuple of 2 elements:

        - Dictionary with
            - Key: Name of the ccbar sample
            - Value: ROOT dataframe after the selection

        - Concatenation of unique identifiers
        '''
        d_rdf    = {}
        full_uid = ''
        for sample in self._l_sample:
            gtr        = RDFGetter(sample=sample, trigger=self._trig)
            rdf        = gtr.get_rdf()
            uid        = gtr.get_uid()
            rdf, uid   = self._filter_rdf(rdf=rdf, sample=sample, uid=uid)

            d_rdf[sample] = rdf
            full_uid     += uid

        return d_rdf, full_uid
    #-----------------------------------------------------------
    def _get_samples_df(self) -> dict[str,pnd.DataFrame]:
        '''
        Returns
        ------------------
        Dictionary with:

        - Key: Name of ccbar sample
        - Value: Pandas dataframe with only the needed columns
        '''
        d_df = {}
        log.debug('Building pandas dataframes:')
        for sample, rdf in self._d_rdf.items():
            log.debug(f'    {sample}')

            rep = rdf.Report()
            rep.Print()

            l_var      = [ name.c_str() for name in rdf.GetColumnNames() if self._need_var( name.c_str() )]
            data       = rdf.AsNumpy(l_var)
            df         = pnd.DataFrame(data)
            df['proc'] = sample

            d_df[sample] = df

        return d_df
    #-----------------------------------------------------------
    def _add_dec_weights(self, sample : str, df : pnd.DataFrame) -> pnd.DataFrame:
        if len(df) == 0:
            return df

        dec = self._d_wg['dec']

        if   dec == 1:
            log.debug(f'Adding decay weights to: {sample}')
            df['wgt_dec'] = df.apply(inclusive_decays_weights.read_weight, args=('L1', 'L2', 'H'), axis=1)
        elif dec == 0:
            log.warning(f'Not using decay weights in: {sample}')
            df['wgt_dec'] = 1.
        else:
            raise ValueError(f'Invalid value of wgt_dec: {dec}')

        arr_wgt      = df.wgt_dec.to_numpy()
        arr_wgt      = self._normalize_weights(arr_wgt)
        df['wgt_dec']= arr_wgt

        return df
    #-----------------------------------------------------------
    def _add_sam_weights(self, df : pnd.DataFrame) -> pnd.DataFrame:
        if len(df) == 0:
            return df

        sam = self._d_wg['sam']

        if   sam == 1:
            log.debug('Adding sample weights')
            obj           = inclusive_sample_weights(df)
            df['wgt_sam'] = obj.get_weights()
        elif sam == 0:
            log.warning('Not using sample weights')
            df['wgt_sam'] = 1.
        else:
            raise ValueError(f'Invalid value of wgt_sam: {sam}')

        arr_wgt      = df.wgt_sam.to_numpy()
        arr_wgt      = self._normalize_weights(arr_wgt)
        df['wgt_sam']= arr_wgt

        return df
    #-----------------------------------------------------------
    def _check_weights(self):
        try:
            [(k1, v1), (k2, v2)] = self._d_wg.items()
        except:
            log.error(f'Cannot extract two weight flags from: {self._d_wg}')
            raise

        if ([k1, k2] != ['dec', 'sam'])  and ([k1, k2] != ['sam', 'dec']):
            raise ValueError(f'Invalid weight keys: {k1}, {k2}')

        if (v1 not in [0, 1]) or (v2 not in [0, 1]):
            raise ValueError(f'Invalid weight values: {v1}, {v2}')
    #-----------------------------------------------------------
    def _check_valid(self, var, l_var, name):
        if var not in l_var:
            log.error(f'Value for {name}, {var}, is not valid')
            raise ValueError
    #-----------------------------------------------------------
    def _get_match_str(self) -> dict[str,str]:
        '''
        Returns
        ----------------
        _selection_ needed to split the charmonium sample into components
        for plotting
        '''
        if   self._q2bin == 'jpsi':
            d_match = self._get_match_str_jpsi()
        elif self._q2bin == 'psi2':
            d_match = self._get_match_str_psi2()
        elif self._q2bin in ['low', 'central', 'high']:
            d_match = self._get_match_str_psi2()
        else:
            raise ValueError(f'Invalid q2bin: {self._q2bin}')

        return d_match
    #-----------------------------------------------------------
    def _get_match_str_jpsi(self) -> dict[str,str]:
        bd          = '(abs(B_TRUEID) == 511)'
        bp          = '(abs(B_TRUEID) == 521)'
        bs          = '(abs(B_TRUEID) == 531)'

        d_cut                                  = {}
        d_cut[r'$B_d\to c\bar{c}(\to ee)H_s$'] = bd
        d_cut[r'$B^+\to c\bar{c}(\to ee)H_s$'] = bp
        d_cut[r'$B_s\to c\bar{c}(\to ee)H_s$'] = bs

        return d_cut
    #-----------------------------------------------------------
    def _get_match_str_psi2(self) -> dict[str,str]:
        bd          = '(abs(B_TRUEID) == 511)'
        bp_psjp     = '(abs(B_TRUEID) == 521) & (abs(Jpsi_TRUEID) == 443) & (abs(Jpsi_MC_MOTHER_ID) == 100443) & (abs(Jpsi_MC_GD_MOTHER_ID) == 521) & (abs(H_MC_MOTHER_ID) == 521)'
        bs          = '(abs(B_TRUEID) == 531)'

        neg_bp_psjp = bp_psjp.replace('==', '!=').replace('&' , '|')
        bp_ex       = f'(abs(B_TRUEID) == 521) & ({neg_bp_psjp})'

        d_cut       = {}
        d_cut[r'$B^+\to \psi(2S)(\to J/\psi+X)H_{s}$'] = bp_psjp
        d_cut[r'$B^+\to c\bar{c}(\to ee)H_s$']         = bp_ex
        d_cut[r'$B_d\to c\bar{c}(\to ee)H_s$']         = bd
        d_cut[r'$B_s\to c\bar{c}(\to ee)H_s$']         = bs

        return d_cut
    #-----------------------------------------------------------
    def _get_match_str_psi2_large(self) -> dict[str,str]:
        '''
        Returns dictionary needed to split mix of MC inclusive samples
        '''
        # pylint: disable=too-many-locals

        bp_psjp     = '(abs(Jpsi_MC_MOTHER_ID) == 100443) & (abs(Jpsi_MC_GD_MOTHER_ID) == 521) & (abs(H_MC_MOTHER_ID) == 521)'
        bd_psks     = '(abs(Jpsi_MC_MOTHER_ID) ==    511) & (abs(H_MC_MOTHER_ID) == 313) & (abs(H_MC_GD_MOTHER_ID) == 511) & (abs(Jpsi_TRUEID) == 100443)'
        bp_psks     = '(abs(Jpsi_MC_MOTHER_ID) ==    521) & (abs(H_MC_MOTHER_ID) == 323) & (abs(H_MC_GD_MOTHER_ID) == 521) & (abs(Jpsi_TRUEID) == 100443)'

        neg_bp_psjp = bp_psjp.replace('==', '!=').replace('&' , '|')
        neg_bd_psks = bd_psks.replace('==', '!=').replace('&' , '|')
        neg_bp_psks = bp_psks.replace('==', '!=').replace('&' , '|')

        bp_jpkp     = '(abs(B_TRUEID) == 521) & (abs(H_TRUEID) == 321) & (abs(Jpsi_TRUEID) == 443)'
        bd_jpkp     = '(abs(B_TRUEID) == 511) & (abs(H_TRUEID) == 321) & (abs(Jpsi_TRUEID) == 443)'

        bp_jpkp_ex  = f'({bp_jpkp}) & ({neg_bp_psjp}) & ({neg_bd_psks}) & ({neg_bp_psks})'
        bd_jpkp_ex  = f'({bd_jpkp}) & ({neg_bp_psjp}) & ({neg_bd_psks}) & ({neg_bp_psks})'

        neg_bp_jpkp = bp_jpkp.replace('==', '!=').replace('&' , '|')
        neg_bd_jpkp = bd_jpkp.replace('==', '!=').replace('&' , '|')


        bs          = '(abs(B_TRUEID) == 531)'
        neg_bs      = '(abs(B_TRUEID) != 531)'

        none        = f'({neg_bp_jpkp}) & ({neg_bd_jpkp}) & ({neg_bp_psjp}) & ({neg_bd_psks}) & ({neg_bp_psks}) & ({neg_bs})'

        d_cut            = {}
        d_cut['bp_psjp'] = bp_psjp
        d_cut['bp_psks'] = bp_psks
        d_cut['bp_jpkp'] = bp_jpkp_ex

        d_cut['bd_psks'] = bd_psks
        d_cut['bd_jpkp'] = bd_jpkp_ex

        d_cut['bs']      = bs

        d_cut['unmatched'] = none

        return d_cut
    #-----------------------------------------------------------
    def _get_match_str_psi2_all(self) -> dict[str,str]:
        d_cut           = {}
        d_cut['jpsi']   = '(Jpsi_TRUEID == 443)'
        d_cut['nojpsi'] = '(Jpsi_TRUEID != 443)'

        return d_cut
    #-----------------------------------------------------------
    def _print_wgt_stat(self, arr_wgt):
        l_wgt = arr_wgt.tolist()
        s_wgt = set(l_wgt)

        log.debug('-' * 20)
        log.debug(f'{"Frequency":<10}{"Weight":>10}')
        for wgt in s_wgt:
            nwgt = numpy.count_nonzero(wgt == arr_wgt)
            log.debug(f'{nwgt:<10}{wgt:>10.3}')
    #-----------------------------------------------------------
    def _normalize_weights(self, arr_wgt):
        tot_wgt = arr_wgt.sum()
        num_wgt = arr_wgt.shape[0]
        fact    = num_wgt / tot_wgt
        arr_wgt = fact * arr_wgt

        return arr_wgt
    #-----------------------------------------------------------
    def _filter_mass(self, df : pnd.DataFrame, mass : str, obs):
        ([[minx]], [[maxx]]) = obs.limits

        cut   = f'({minx} < {mass}) & ({mass} < {maxx})'
        log.debug(f'Applying: {cut}')
        inum  = df.shape[0]
        df    = df.query(cut)
        fnum  = df.shape[0]

        self._d_fstat[cut] = inum, fnum

        return df
    #-----------------------------------------------------------
    def _filter_cut(self, cut : str) -> pnd.DataFrame:
        if cut is None:
            log.debug('Not applying any cut')
            return self._df

        log.info(f'Applying cut: {cut}')
        inum = self._df.shape[0]
        df   = self._df.query(cut)
        fnum = df.shape[0]

        self._d_fstat[cut] = inum, fnum

        return df
    #-----------------------------------------------------------
    def _get_identifier(self, mass : str, cut : str, **kwargs) -> str:
        cwargs = copy.deepcopy(kwargs)
        del cwargs['obs']

        swgt = json.dumps(self._d_wg , sort_keys=True)
        scwg = json.dumps(cwargs     , sort_keys=True)

        l_d_sel   = [ sel.selection(trigger=self._trig, q2bin=self._q2bin, process=sample) for sample in self._l_sample ]
        l_element = [
                swgt,
                self._trig,
                self._q2bin,
                mass,
                scwg,           # Stringified keyword arguments
                self._l_sample, # ccbar cocktail sample names
                l_d_sel,        # list of selections, one for each ccbar cocktail sample
                cut]

        hsh  = hashing.hash_object(l_element)

        return hsh
    #-----------------------------------------------------------
    def _path_from_identifier(self, identifier : str) -> str:
        dir_path = '/tmp/cache/prec'
        os.makedirs(dir_path, exist_ok=True)

        return f'{dir_path}/pdf_{identifier}.json'
    #-----------------------------------------------------------
    def _drop_before_saving(self, df : pnd.DataFrame) -> pnd.DataFrame:
        l_needed = self._l_mass + ['wgt_br', 'wgt_dec', 'wgt_sam']
        l_drop   = [ name for name in df.columns if  name not in l_needed ]
        df       = df.drop(l_drop, axis=1)

        return df
    #-----------------------------------------------------------
    def _get_pdf(
        self,
        mass           : str,
        df             : pnd.DataFrame,
        component_name : str,
        **kwargs) -> zpdf|None:
        '''
        Parameters
        ------------------
        name    : Latex name of PDF component
        mass    : Mass, with values in:
            mass     : Non constrained B mass
            mass_jpsi: Jpsi constrained B mass
            mass_psi2: Psi2S constrained B mass
        df      : DataCorresponding to given ccbar component
        **kwargs: These are all arguments for KDE1DimISJ or KDE1DimFFT

        Returns
        ------------------
        Either:
        None   : If there are fewer than _min_entries
        KDE PDF: Otherwise
        '''
        # This kwargs reffers to this particular PDF
        kwargs         = copy.deepcopy(kwargs)
        pdf_name       = kwargs['name']
        slug           = slugify.slugify(pdf_name, lowercase=False)
        kwargs['name'] = component_name

        arr_mass = df[mass     ].to_numpy()
        arr_wgt  = df['wgt_br' ].to_numpy()
        obs      = kwargs['obs']

        nentries = self._yield_from_arrays(arr_mass=arr_mass, arr_weight=arr_wgt, obs=obs)
        if nentries < self._min_entries:
            log.warning(f'Found fewer than {self._min_entries}: {nentries}, skipping PDF {component_name}')
            return None

        log.debug(f'Building PDF with {nentries} entries for {component_name}')

        pdf          = self._pdf_from_df(df=df, mass=mass, **kwargs)
        pdf.arr_mass = arr_mass
        pdf.arr_wgt  = arr_wgt
        pdf.arr_sam  = df['wgt_sam'].to_numpy()
        pdf.arr_dec  = df['wgt_dec'].to_numpy()

        if not is_pdf_usable(pdf):
            log.warning(f'PDF {component_name} is not usable')
            return None

        PRec.plot_pdf(
            pdf,
            title  =component_name,
            name   =component_name,
            out_dir=f'{self._out_path}/{slug}')

        return pdf
    #-----------------------------------------------------------
    def _pdf_from_df(
        self,
        df   : pnd.DataFrame,
        mass : str,
        **kwargs) -> zpdf:
        '''
        Will build KDE from dataframe with information needed

        Parameters
        ---------------
        df     : DataFrame with weights and masses, the weight is assumed to be in 'wgt_br'
        mass   : Name of the column with mass to be fitted
        kwargs : Keyword arguments meant to be passed to KDE1Dim*
        '''
        arr_mass = df[mass    ].to_numpy()
        arr_wgt  = df['wgt_br'].to_numpy()
        arr_wgt  = arr_wgt.astype(float)

        try:
            pdf = self._build_kde(arr_mass=arr_mass, arr_wgt=arr_wgt, **kwargs)
        except Exception as exc:
            for setting, value in kwargs.items():
                if not isinstance(value, (str,float,int)):
                    log.info(f'{setting:<30}{"--->"}')
                    log.info(value)
                else:
                    log.info(f'{setting:<30}{value:<30}')

            raise Exception('Failed to build KDE') from exc

        return pdf
    #-----------------------------------------------------------
    def _build_kde(
            self,
            arr_mass : numpy.ndarray,
            arr_wgt  : numpy.ndarray, **kwargs) -> zpdf:
        '''
        Parameters
        --------------
        arr_xxx: Contains mass and weights needed for KDE

        Returns
        --------------
        Either FFT or ISJ KDE
        '''
        if log.getEffectiveLevel() < 20:
            log.debug('Using fitting options:')
            pprint.pprint(kwargs)

        nentries = len(arr_mass)
        if nentries > self._min_isj_entries:
            log.debug('Using ISJ KDE for high statistics sample')
            if 'bandwidth' in kwargs: # ISJ does not accept this argument
                del kwargs['bandwidth']

            pdf = zfit.pdf.KDE1DimISJ(arr_mass, weights=arr_wgt, **kwargs)
        else:
            log.debug('Using FFT KDE for low statistics sample')
            pdf = zfit.pdf.KDE1DimFFT(arr_mass, weights=arr_wgt, **kwargs)

        return pdf
    #-----------------------------------------------------------
    def _print_cutflow(self) -> None:
        log.debug('-' * 50)
        log.debug(f'{"Cut":<30}{"Total":<20}{"Passed":<20}')
        log.debug('-' * 50)
        for cut, (inum, fnum) in self._d_fstat.items():
            log.debug(f'{cut:<30}{inum:<20}{fnum:<20}')
        log.debug('-' * 50)
    #-----------------------------------------------------------
    def _frac_from_pdf(self, pdf : zpdf, frc : float) -> zpar:
        name = pdf.name
        slug = slugify.slugify(name, lowercase=False)
        par  = zfit.param.Parameter(f'f_{slug}', frc, 0, 1)

        par.floating = False

        return par
    #-----------------------------------------------------------
    def _yield_in_range(self, pdf : zpdf) -> float:
        '''
        Parameters
        ---------------
        pdf: ZFit KDE PDF with array of weights and masses that were used to make it, attached

        Returns
        ---------------
        The mass and weights are defined in the WHOLE range. This method extracts the yields
        in the observable range. Needed to calculate fractions of componets, used to put
        ccbar stuff together
        '''
        obs = pdf.space
        wgt = pdf.arr_wgt
        mas = pdf.arr_mass

        return self._yield_from_arrays(arr_mass=mas, arr_weight=wgt, obs=obs)
    #-----------------------------------------------------------
    def _yield_from_arrays(
        self,
        obs        : zobs,
        arr_mass   : numpy.ndarray,
        arr_weight : numpy.ndarray) -> float:

        minx, maxx = sut.range_from_obs(obs=obs)

        mask= (minx < arr_mass) & (arr_mass < maxx)
        wgt = arr_weight[mask]

        return sum(wgt)
    #-----------------------------------------------------------
    def _get_full_pdf(
        self,
        mass : str,
        d_df : dict[str,pnd.DataFrame],
        **kwargs) -> zpdf|None:
        '''
        Parameters
        -------------------
        mass  : Name of the column in the dataframe, which will be used to build KDE
        kwars : Key word arguments needed to build KDE PDF
        d_df  : Dictionary with:
            Key  : Latex name of component, not necessarily Bu/Bd... This was re-split
            Value: Dataframe with data to fit

        Returns
        -------------------
        Full pdf, i.e. all ccbar components added
        '''
        l_pdf     = [ self._get_pdf(mass = mass, component_name = ltex, df = df, **kwargs) for ltex, df in d_df.items()                    ]
        l_pdf     = [                                                                  pdf for      pdf in l_pdf        if pdf is not None ]
        l_wgt_yld = [ self._yield_in_range(pdf=pdf)                                        for      pdf in l_pdf                           ]
        l_frc     = [ wgt_yld / sum(l_wgt_yld)                                             for  wgt_yld in l_wgt_yld                       ]
        l_yld     = [ self._frac_from_pdf(pdf=pdf, frc=frc)                                for pdf, frc in zip(l_pdf, l_frc)               ]

        if   len(l_pdf) >= 2:
            pdf   = zfit.pdf.SumPDF(l_pdf, fracs=l_yld, name='ccbar PRec')
        elif len(l_pdf) == 1:
            [pdf] = l_pdf
        else:
            log.warning('No PDF can be built with dataset')
            return None

        l_arr_mass   = [ pdf.arr_mass for pdf in l_pdf ]
        l_arr_wgt    = [ pdf.arr_wgt  for pdf in l_pdf ]
        l_arr_sam    = [ pdf.arr_sam  for pdf in l_pdf ]
        l_arr_dec    = [ pdf.arr_dec  for pdf in l_pdf ]

        pdf.arr_mass = numpy.concatenate(l_arr_mass)
        pdf.arr_wgt  = numpy.concatenate(l_arr_wgt )
        pdf.arr_dec  = numpy.concatenate(l_arr_dec )
        pdf.arr_sam  = numpy.concatenate(l_arr_sam )

        return pdf
    #-----------------------------------------------------------
    def get_sum(self, mass : str, name='unnamed', **kwargs) -> Union[zpdf,None]:
        '''Provides extended PDF that is the sum of multiple KDEs representing PRec background

        Parameters:
        mass (str) : Defines which mass constrain to use, choose between "B_M", "B_const_mass_M", "B_const_mass_psi2S_M"
        name (str) : PDF name
        **kwargs   : Arguments meant to be taken by zfit KDE1DimFFT

        Returns:
        zfit.pdf.SumPDF instance
        '''
        kwargs['name'] = name
        slug           = slugify.slugify(name, lowercase=False)

        l_ltex      = list(self._d_match) # Get component names in latex and map them to parquet files to save
        d_ltex_slug = { ltex : slugify.slugify(ltex, lowercase=False) for ltex       in l_ltex }
        d_path      = { ltex : f'{self._out_path}/{slug}.parquet'     for ltex, slug in d_ltex_slug.items() }

        if self._copy_from_cache():
            log.info(f'Data found cached, reloading from {self._out_path}')
            d_df = { ltex : pnd.read_parquet(path) for ltex , path in d_path.items() }
            pdf        = self._get_full_pdf(mass=mass, d_df=d_df, **kwargs)

            PRec.plot_pdf(
                pdf,
                title  =name,
                name   =name,
                out_dir=f'{self._out_path}/{slug}')

            return pdf

        log.info(f'Recalculating, cached data not found in: {self._out_path}')

        d_df = self._get_df()
        pdf  = self._get_full_pdf(mass=mass, d_df=d_df, **kwargs)

        # Save dataframes before caching
        # Cache at the very end
        log.info('Saving dataframes:')
        for ltex, df in d_df.items():
            path = d_path[ltex]
            log.info(f'   {path}')
            df.to_parquet(path)

        PRec.plot_pdf(
            pdf,
            title  =name,
            name   =name,
            out_dir=f'{self._out_path}/{slug}')

        self._cache()

        return pdf
    #-----------------------------------------------------------
    @staticmethod
    def plot_pdf(
            pdf     : zpdf|None,
            name    : str,
            out_dir : str,
            title   : str        = '',
            maxy    : float|None = None) -> None:
        '''
        Utility method, meant to plot PDF after it was built

        Parameters
        ------------------
        pdf    : PDF
        neme   : used to name the PNG file as {name}.png
        title  : Title for plots, will be appended after number of entries
        maxy   : Will be used to plot fit properly in case labels overlap
        out_dir: Directory where plots will go
        '''

        if pdf is None:
            log.warning(f'PDF {name} not build, not plotting')
            return

        arr_mass = pdf.arr_mass
        arr_wgt  = pdf.arr_wgt
        arr_sam  = pdf.arr_sam
        arr_dec  = pdf.arr_dec

        obj = ZFitPlotter(data=arr_mass, model=pdf, weights=arr_wgt)
        obj.plot(stacked=True)

        obj.axs[0].set_title(f'#Entries: {arr_mass.size}; {title}')

        if maxy is not None:
            obj.axs[0].set_ylim(bottom=0, top=maxy)

        obj.axs[0].axvline(x=5080, linestyle=':')
        obj.axs[0].axvline(x=5680, linestyle=':')
        obj.axs[0].axvline(x=5280, label=r'$B^+$', color='gray', linestyle='--')

        obj.axs[1].set_ylim(-5, +5)
        obj.axs[1].axhline(y=-3, color='red')
        obj.axs[1].axhline(y=+3, color='red')
        obj.axs[1].set_label('M$(B^+)$[MeV/${}_{c^2}$]')

        os.makedirs(out_dir, exist_ok=True)

        slug = slugify.slugify(name, lowercase=False)

        plot_path = f'{out_dir}/{slug}.png'
        log.info(f'Saving to: {plot_path}')
        plt.savefig(plot_path)
        plt.close('all')

        plt.hist(arr_sam, bins=30, label='sample', histtype='step', linestyle='-' )
        plt.hist(arr_dec, bins=30, label='decay' , histtype='step', linestyle='--')
        plt.hist(arr_wgt, bins=30, label='Total' , histtype='step', linestyle=':' )

        plt.legend()
        plt.title(title)
        plt.savefig(f'{out_dir}/{slug}_wgt.png')
        plt.close('all')

        text_path = plot_path.replace('png', 'txt')
        sut.print_pdf(pdf, txt_path=text_path)
    #-----------------------------------------------------------
    @staticmethod
    @contextmanager
    def apply_setting(use_cache : bool):
        '''
        Used to override default behaviour

        use_cache : If False (default is True) will recalculate the PDF
        '''
        old_val = PRec.use_cache
        try:
            PRec.use_cache = use_cache
            yield
        finally:
            PRec.use_cache = old_val
#-----------------------------------------------------------
