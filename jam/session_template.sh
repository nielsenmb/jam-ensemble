#!/bin/bash
#SBATCH --ntasks NTASKS
#SBATCH --nodes 1
#SBATCH --time TIME
#SBATCH --qos QOS
#SBATCH --mail-type NONE
#SBATCH --job-name=pbj_IDX
#SBATCH --account=ACCOUNT
#SBATCH --constraint cascadelake

set -e

module purge; module load bluebear # this line is required
module load bear-apps/2019b
module load GCC/8.3.0
module load Theano/1.0.4-foss-2019b-Python-3.7.4
module load Python/3.7.4-GCCcore-8.3.0

source VENV_PATH/bin/activate

python -u PY_PATH START END
