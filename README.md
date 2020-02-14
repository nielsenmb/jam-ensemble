# jam-ensemble

Peakbagging with [PBjam](https://github.com/grd349/PBjam) on many stars. This repo is configured for use on [BlueBEAR](https://intranet.birmingham.ac.uk/it/teams/infrastructure/research/bear/bluebear/index.aspx) (adapted from work by Martin Nielsen).

## Getting started

1. Clone the repo.

   ```none
   % module load bear-apps/2019b
   % module load git/2.23.0-GCCcore-8.3.0-nodocs
   % git clone https://github.com/alexlyttle/jam-ensemble.git
   ```

2. Load the following python module:

   ```none
   % module load GCC/8.3.0
   % module load Python/3.7.4-GCCcore-8.3.0
   ```

3. Create virtual environment with requirements, e.g.

   ```none
   % virtualenv ~/.virtualenvs/my_venv
   % source ~/.virtualenvs/my_venv/bin/activate
   (my_venv) % pip install -r jam-ensemble/requirements.txt
   ```

4. Copy `jam-ensemble/jam` to a different directory, e.g.

   ```none
   % cp -r jam-ensemble/jam /path/to/example-jam
   ```

5. Edit `config.yaml` with appropriate configurations (e.g. paths and script options).

6. Run `make_scripts.py` to generate scripts for each BlueBEAR job.

7. Run `submit_all` to submit the jobs

   ```none
   % submit_all
   ```

8. Sit back and relax while it all works without fault.\*

\* Disclaimer: [Murphy's Law](https://en.wikipedia.org/wiki/Murphy%27s_law)
