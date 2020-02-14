# jam-ensemble

Peakbagging with [PBjam](https://github.com/grd349/PBjam) on many stars. This repo is configured for use on [BlueBEAR](https://intranet.birmingham.ac.uk/it/teams/infrastructure/research/bear/bluebear/index.aspx) (adapted from work by Martin Nielsen).

1. Clone the repo.

2. Install requirements, e.g.

   ```shell
   % pip install -r requirements.txt
   ```

3. Copy `jam-ensemble/jam` into your working directory.

4. Edit `config.yaml` with appropriate configurations (e.g. paths and script options).

5. Run `make_scripts.py` to generate scripts for each BlueBEAR job.

6. Run `pbscript.sh` to submit the jobs

   ```shell
   % sbatch pbscript.sh
   ```

7. Sit back and relax while it all works without fault.\*

\* Disclaimer: [Murphy's Law](https://en.wikipedia.org/wiki/Murphy%27s_law)
