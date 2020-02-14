#!/usr/bin/env python3
import pandas as pd
import numpy as np
from yaml import safe_load
import os
import warnings

config_keys = ['n_cores', 'path_to_input_data']
bear_keys = ['account', 'qos', 'ntasks_per_job', 'path_to_venv']

with open('config.yml') as stream:
    options = safe_load(stream)
    config = options['session']
    bear = options['bluebear']
    if not all([key in config.keys() for key in config_keys]):
        raise KeyError(f'File config.yml must contain options for all of {config_keys}.')
    if not all([key in bear.keys() for key in bear_keys]):
        raise KeyError(f'File config.yml must contain options for all of {bear_keys}.')

ncores = config['n_cores']
njobs = len(pd.read_csv(config['path_to_input_data']))

if ncores > njobs:
    ncores = njobs

print(f'Njobs : {njobs}, Ncores : {ncores}')

with open('session_template.sh') as fin:
    template = fin.read()

njobs_per_script = np.floor(njobs / ncores)
if njobs_per_script < 1:
    njobs_per_script = 1

start = np.arange(ncores) * njobs_per_script
end = start + njobs_per_script

if not os.path.exists('scripts'):
    os.mkdir('scripts')
elif len(os.listdir('scripts')) > 0:
    warnings.warn('Directory /scripts is not empty, consider removing ' +
                  'unwanted files and rerunning this script.')

for idx, st in enumerate(start):
    sr = template.replace('START', str(int(st)))
    sr = sr.replace('END', str(int(st + njobs_per_script)))
    sr = sr.replace('IDX', str(idx))
    sr = sr.replace('NTASKS', str(int(bear['ntasks_per_job'])))
    sr = sr.replace('QOS', str(bear['qos']))
    sr = sr.replace('ACCOUNT', str(bear['account']))
    sr = sr.replace('VENV_PATH', str(bear['path_to_venv']))
    sr = sr.replace('PY_PATH', os.path.join(os.getcwd(), 'run_session.py'))

    with open(f'scripts/session_{idx}.sh', 'w') as file:
        file.write(sr)
