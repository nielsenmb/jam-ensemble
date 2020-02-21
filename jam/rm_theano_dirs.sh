#!/bin/bash
#SBATCH --ntasks 2
#SBATCH --time 30:0
#SBATCH --qos bbdefault
#SBATCH --mail-type NONE
#SBATCH --job-name=rm_theano_dirs

rm -r logs/.theano
echo Done.
