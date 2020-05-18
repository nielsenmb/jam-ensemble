#!/usr/bin/env python3
import pandas as pd
import numpy as np
from yaml import safe_load
import os
import warnings

config_keys = ['path_to_input_data']
bear_keys = ['n_jobs', 'account', 'qos', 'ntasks_per_job', 'path_to_venv', 'time_per_job']

with open('config.yml') as stream:
    options = safe_load(stream)
    config = options['session']
    bear = options['bluebear']
    if not all([key in config.keys() for key in config_keys]):
        raise KeyError(f'File config.yml must contain options for all of {config_keys}.')
    if not all([key in bear.keys() for key in bear_keys]):
        raise KeyError(f'File config.yml must contain options for all of {bear_keys}.')



n_jobs = bear['n_jobs']
n_stars = len(pd.read_csv(config['path_to_input_data']))

if n_jobs > n_stars:
    n_jobs = n_stars

print(f'n_stars : {n_stars}, n_jobs : {n_jobs}')

with open('session_template.sh') as fin:
    template = fin.read()

if n_stars < n_jobs:
    n_jobs = n_stars
    
indexes = np.array([round(x) for x in np.linspace(0, n_stars, n_jobs+1)])

if not os.path.exists('scripts'):
    os.mkdir('scripts')
elif len(os.listdir('scripts')) > 0:
    warnings.warn('Directory /scripts is not empty, consider removing ' +
                  'unwanted files and rerunning this script.')

for i in range(n_jobs):
    sr = template.replace('START', str(int(indexes[i])))
    sr = sr.replace('END', str(int(indexes[i+1])))
    sr = sr.replace('IDX', str(i))
    sr = sr.replace('NTASKS', str(int(bear['ntasks_per_job'])))
    sr = sr.replace('QOS', str(bear['qos']))
    sr = sr.replace('ACCOUNT', str(bear['account']))
    sr = sr.replace('VENV_PATH', str(bear['path_to_venv']))
    sr = sr.replace('PY_PATH', os.path.join(os.getcwd(), 'run_session.py'))
    sr = sr.replace('TIME', str(bear['time_per_job']))
    sr = sr.replace('COMPDIR', os.path.join(*[config['output_data_dir'], '.theano', 'PID' + str(int(indexes[i]))]))

    with open(f'scripts/session_{i}.sh', 'w') as file:
        file.write(sr)
