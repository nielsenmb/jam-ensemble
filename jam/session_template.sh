#!/bin/bash
#SBATCH --ntasks NTASKS
#SBATCH --nodes 1
#SBATCH --time 12:0:0
#SBATCH --qos QOS
#SBATCH --mail-type NONE
#SBATCH --job-name=pbj_IDX
#SBATCH --account=ACCOUNT
#SBATCH --constraint cascadelake

set -e

module purge; module load bluebear # this line is required
module load bear-apps/2019b
module load Python/3.7.4-GCCcore-8.3.0

source VENV_PATH/bin/activate

python -u PY_PATH START END
