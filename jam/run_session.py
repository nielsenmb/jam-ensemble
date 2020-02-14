import matplotlib
matplotlib.use('Agg')

import pandas as pd
import sys
import os
from yaml import safe_load

print(sys.argv)

config_keys = ['path_to_input_data', 'mission', 'lightkurve_download_dir',
               'output_data_dir', 'n_orders', 'make_plots', 'kde_bandwidth']

with open('config.yml') as stream:
    config = safe_load(stream)['session']
    if not all([key in config.keys() for key in config_keys]):
        raise KeyError(f'File config.yml must contain options for all of {config_keys}.')

df = pd.read_csv(config['path_to_input_data'])

# Force theano to compile to a unique directory for each job!
compile_dir = os.path.join(*[config['output_data_dir'], '.theano', 'PID' + sys.argv[1]])
if not os.path.exists(compile_dir):
    os.mkdir(compile_dir)
os.environ["THEANO_FLAGS"] = 'base_compiledir=' + compile_dir

from jam_session import jam

if len(sys.argv) == 3:
    df = df[int(sys.argv[1]):int(sys.argv[2])]

print(df)

jam_session = jam(dictlike=df, mission=config['mission'],
                  download_dir=config['lightkurve_download_dir'],
                  path=config['output_data_dir'])

jam_session(norders=config['n_orders'], make_plots=config['make_plots'],
            bw_fac=config['kde_bandwidth'])

print('Finished.')
