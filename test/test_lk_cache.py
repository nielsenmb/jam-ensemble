import lightkurve as lk

LK_CACHE_DIR = 'test/.lightkurve-cache'
ID = 'KIC4448777'
MISSION = 'Kepler'

lcc = lk.search_lightcurvefile(ID, mission=MISSION).download_all(download_dir=LK_CACHE_DIR)
