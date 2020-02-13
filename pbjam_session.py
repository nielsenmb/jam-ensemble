import matplotlib
matplotlib.use('Agg')

import pandas as pd
import sys
import os

print(sys.argv)

df = pd.read_csv('/rds/projects/n/nielsemb-plato-peakbagging/pbjam/MS_SG_tgts_to_fit.csv')
ddir = '/rds/projects/n/nielsemb-plato-peakbagging/pbjam/PBjamResults/MSSG'
download_dir = '/rds/projects/n/nielsemb-plato-peakbagging/pbjam/data'

# Force theano to compile to a unique directory for each job!
compile_dir = os.path.join(*[ddir, '.theano', 'PID'+sys.argv[1]]) #ddir + '.theano' + os.sep + 'PID' + sys.argv[1]
if not os.path.exists(compile_dir):
    os.mkdir(compile_dir)
os.environ["THEANO_FLAGS"] = 'base_compiledir=' + compile_dir

from jam_session import jam

if len(sys.argv) == 3:
    df = df[int(sys.argv[1]):int(sys.argv[2])]


# print(df)

# numaxs = [[n, err] for n, err in zip(df.numax, df.numax_err)]
# cadences = []
# for numax in numaxs:
#     if numax[0] > 300.0:
#         cadences.append('short')
#     else:
#         cadences.append('long')
# df['cadence'] = 'short'

jam_sess = jam(dictlike=df,
                   use_cached=False,
		   download_dir=download_dir,
                   path=ddir,
		   )

jam_sess(norders=8, make_plots=True, nthreads=1, bw_fac=5)

print('Finished : TODO')
