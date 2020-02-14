'''jam_session.py
Author(s)
---------
Alex Lyttle

Description
-----------
This script should be copied into your working directory and the
capitalised variables changed as required. Input data should be in CSV format
as required by `dictlike` in `pbjam.session` with column headers as follows:

ID,numax,numax_err,dnu,dnu_err,teff,teff_err,bp_rp,bp_rp_err,(timeseries),(psd)

where those in brackets are optional. Read 
https://pbjam.readthedocs.io/en/latest/example-session.html for more
information.

Currently, this script crudely sub-classes `pbjam.session` and modifies a 
helper function to catch errors when downloading lightcurves (e.g. if it is not
available).

Some of this code is copied from 
https://github.com/grd349/PBjam/blob/master/pbjam/session.py

'''
import pbjam as pb
import warnings
import pandas as pd
import os
from pbjam.session import *

# failed_lk_query = pd.DataFrame()

def append_failed_targets(path, id, exception):
    df = pd.DataFrame()
    df.at[id, 'exception'] = str(exception)
    full_path = os.path.join(path, 'failed_targets.csv')
    
    if os.path.isfile(full_path):
        df.to_csv(full_path, mode='a', header=False)
    else:
        df.to_csv(full_path, index_label='ID')

def lc_to_lk(vardf, download_dir, path, use_cached=True):
    """ Add 'try and except' brute force to avoid errors.
    """
    failed_lk_query = pd.DataFrame()
    
    tinyoffset = 1  # to avoid cases LC median = 0 (lk doesn't like it)
    key = 'timeseries'
    for i, id in enumerate(vardf['ID']):
        if isinstance(vardf.loc[i, key], str):
            t, d = np.genfromtxt(vardf.loc[i, key], usecols=(0, 1)).T
            d += tinyoffset
            vardf.at[i, key] = arr_to_lk(t, d, vardf.loc[i, 'ID'], key)
        elif not vardf.loc[i, key]:
            if vardf.loc[i, 'psd']:
                pass
            else:
                D = {x: vardf.loc[i, x] for x in ['cadence', 'month', 'sector',
                                                  'campaign', 'quarter', 
                                                  'mission']}
                # Try to query lightkurve. If error, drop the row
                try:
                    lk_lc = query_lightkurve(id, download_dir, use_cached, D)
                    vardf.at[i, key] = lk_lc
                except Exception as ex:
                    print(f'Lightkurve query failed on {id} due to:\n{ex}\n' +
                          'This target will be removed from the sample.')
                    append_failed_targets(path, id, ex)
                    # failed_lk_query.at[id, 'error'] = str(exc)
                    vardf = vardf.drop(i)

        elif vardf.loc[i, key].__module__ == lk.lightcurve.__name__:
            pass
        else:
            raise TypeError("Can't handle this type of time series object") 
        
        # Ignore key error due to the row being dropped.
        try:
            if vardf.loc[i, key]:
                sort_lc(vardf.loc[i, key])
        except KeyError:
            pass
    
    # failed_lk_query.to_csv(os.path.join(path, 'failed_lk_targets.csv'),
    #                        index_label=f'id')
    
    vardf = vardf.reset_index()  # Resets indices to avoid issues later on.
    return vardf


class jam(session):
    """Sub-class of pbjam.session to bodge catching errors.
        
    """

    def __init__(self, ID=None, numax=None, dnu=None, teff=None, bp_rp=None,
                 timeseries=None, psd=None, dictlike=None, use_cached=False, 
                 cadence=None, campaign=None, sector=None, month=None, 
                 quarter=None, mission=None, path=None, download_dir=None):

        self.stars = []
        self.path = path
        
        # Make sure path exists
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        
        if isinstance(dictlike, (dict, np.recarray, pd.DataFrame, str)):
            if isinstance(dictlike, str):
                vardf = pd.read_csv(dictlike)
            else:
                try:
                    vardf = pd.DataFrame.from_records(dictlike)
                except TypeError:
                    print('Unrecognized type in dictlike. Must be able to ' +
                          'convert to dataframe through ' +
                          'pandas.DataFrame.from_records()')

            if any([ID, numax, dnu, teff, bp_rp]):
                warnings.warn('Dictlike provided as input, ignoring other ' +
                              'input fit parameters.')

            organize_sess_dataframe(vardf)

        elif ID:
            vardf = organize_sess_input(ID=ID, numax=numax, dnu=dnu, teff=teff,
                                        bp_rp=bp_rp, cadence=cadence,
                                        campaign=campaign, sector=sector,
                                        month=month, quarter=quarter, 
                                        mission=mission)
            format_col(vardf, timeseries, 'timeseries')
            format_col(vardf, psd, 'psd')
        
        # Take whatever is in the timeseries column of vardf and make it an
        # lk.lightcurve object or None
        
        vardf = lc_to_lk(vardf, download_dir, self.path, use_cached=use_cached)
        
        # Take whatever is in the timeseries column of vardf and turn it into
        # a periodogram object in the periodogram column.

        lk_to_pg(vardf)

        for i in range(len(vardf)):
            self.stars.append(star(ID=vardf.loc[i, 'ID'],
                                   pg=vardf.loc[i, 'psd'],
                                   numax=vardf.loc[i, ['numax', 'numax_err']].values,
                                   dnu=vardf.loc[i, ['dnu', 'dnu_err']].values,
                                   teff=vardf.loc[i, ['teff', 'teff_err']].values,
                                   bp_rp=vardf.loc[i, ['bp_rp', 'bp_rp_err']].values,
                                   path=path))

        for i, st in enumerate(self.stars):
            if st.numax[0] > st.f[-1]:
                warnings.warn("Input numax is greater than Nyquist frequeny " +
                              "for %s" % (st.ID))

    def __call__(self, bw_fac=1, tune=1500, norders=8, model_type='simple', 
                 verbose=False, nthreads=1, store_chains=False, 
                 make_plots=False):
        """ The doitall script
        Calling session will by default do asymptotic mode ID and peakbagging
        for all stars in the session.
        Parameters
        ----------
        norders : int
            Number of orders to include in the fits
            
        """
        
        self.pb_model_type = model_type

        for i, st in enumerate(self.stars):
            try:
                st(bw_fac=bw_fac, tune=tune, norders=norders, 
                   model_type=self.pb_model_type, verbose=verbose, 
                   make_plots=make_plots, store_chains=store_chains, 
                   nthreads=nthreads)
                
                self.stars[i] = None
                    
            except Exception as ex:
                message = ("Star {0} produced an exception of type {1} " +
                           "occurred. Arguments:\n{2!r}"
                           ).format(st.ID, type(ex).__name__, ex.args)
                print(message)
                # failed_lk_query.at[id, 'error'] = str(ex)
                append_failed_targets(self.path, st.ID, ex)

            
if __name__ == '__main__':
    # Modify capitalised variables below for testing
    PATH_TO_INPUT_DATA = '../test/input/jam_session_test_data.csv'
    OUTPUT_DATA_DIR = '../test/logs'
    LIGHTCURVE_DOWNLOAD_DIR = '.lightkurve-cache'
    MISSION = 'Kepler'
    N_ORDERS = 9  # Number of radial orders to fit about nu_max
    MAKE_PLOTS = True
    
    jam_session = jam(dictlike=PATH_TO_INPUT_DATA, mission=MISSION,
                      download_dir=LIGHTCURVE_DOWNLOAD_DIR,
                      path=OUTPUT_DATA_DIR)

    jam_session(norders=N_ORDERS, make_plots=MAKE_PLOTS)

    # jam_session.failed_lk_query.to_csv(os.path.join(OUTPUT_DATA_DIR,
    #                                    'failed_lk_targets.csv'),
    #                                    index_label=f'id')
