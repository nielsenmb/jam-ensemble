#!/bin/bash
#SBATCH --ntasks 2
#SBATCH --nodes 1
#SBATCH --time 12:0:0
#SBATCH --qos bbdefault
#SBATCH --mail-type NONE
#SBATCH --job-name=pbjIDX
#SBATCH --account=nielsemb-plato-peakbagging
#SBATCH --constraint cascadelake

set -e

module purge; module load bluebear # this line is required
module load Python/3.6.6-foss-2018b
module load future/0.16.0-foss-2018b-Python-3.6.6
module load matplotlib/3.0.0-foss-2018b-Python-3.6.6

#python3 -m pip install -e ~/Software/PBjam --user

python -u /rds/homes/n/nielsemb/repos/BlueBEARSuite/pbjam_session/pbjam_session.py START END
