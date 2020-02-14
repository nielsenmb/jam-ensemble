#!/usr/bin/env python3
import pandas as pd
import numpy as np

ncores = 500
njobs = len(pd.read_csv('/rds/projects/n/nielsemb-plato-peakbagging/pbjam/MS_SG_tgts_to_fit.csv'))

if ncores > njobs:
    ncores = njobs

print(f'Njobs : {njobs}, Ncores : {ncores}')

with open('pbscript.sh') as fin:
    template = fin.read()

njobs_per_script = np.floor(njobs / ncores)
if njobs_per_script < 1:
    njobs_per_script = 1

start = np.arange(ncores) * njobs_per_script
end = start + njobs_per_script

for idx, st in enumerate(start):
    sr = template.replace('START',
                          str(int(st))).replace('END',
                          str(int(st + njobs_per_script)))
    sr = sr.replace('IDX', str(idx))
    with open(f'Scripts/pbscript_{idx}.sh', 'w') as fout:
        fout.write(sr)
