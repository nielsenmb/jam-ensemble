import pbjam as pb
import warnings
import pandas as pd
import os
from pbjam.session import *

PATH_TO_INPUT_DATA = 'test/input/jam_session_test_data.csv'
OUTPUT_DATA_DIR = 'test/output'
LIGHTCURVE_DOWNLOAD_DIR = '.lightkurve-cache'
MISSION = 'Kepler'

failed_lk_query = pd.DataFrame()

def lc_to_lk(vardf, download_dir, use_cached=True):
    """ Add 'try and except' brute force to avoid errors.
    """

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
                except Exception as exc:
                    print(f'Lightkurve query failed on {id} due to:\n{exc}\nThis target will be removed from the sample.')
                    failed_lk_query.at[id, 'error'] = str(exc)
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
        
    vardf.reset_index(inplace=True)  # Resets indices to avoid issues later on.


class jam(session):
    """Sub-class of pbjam.session to bodge catching errors.
        
    """

    def __init__(self, ID=None, numax=None, dnu=None, teff=None, bp_rp=None,
                 timeseries=None, psd=None, dictlike=None, use_cached=False, 
                 cadence=None, campaign=None, sector=None, month=None, 
                 quarter=None, mission=None, path=None, download_dir=None):

        self.stars = []
        
        if isinstance(dictlike, (dict, np.recarray, pd.DataFrame, str)):
            if isinstance(dictlike, str):
                vardf = pd.read_csv(dictlike)
            else:
                try:
                    vardf = pd.DataFrame.from_records(dictlike)
                except TypeError:
                    print('Unrecognized type in dictlike. Must be able to convert to dataframe through pandas.DataFrame.from_records()')

            if any([ID, numax, dnu, teff, bp_rp]):
                warnings.warn('Dictlike provided as input, ignoring other input fit parameters.')

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

        lc_to_lk(vardf, download_dir, use_cached=use_cached)
        
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
                warnings.warn("Input numax is greater than Nyquist frequeny for %s" % (st.ID))
            
if __name__ == '__main__':
    jam_session = jam(dictlike=PATH_TO_INPUT_DATA, mission=MISSION,
                    download_dir=LIGHTCURVE_DOWNLOAD_DIR,
                    path=OUTPUT_DATA_DIR)

    jam_session(norders=9, make_plots=True)

    failed_lk_query.to_csv(os.path.join(OUTPUT_DATA_DIR, 'failed_lk_targets.csv'),
                        index_label=f'{MISSION} ID')
