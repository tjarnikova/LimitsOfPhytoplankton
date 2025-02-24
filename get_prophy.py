### get prophy for n atl only
import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt
import xarray as xr
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')
from importlib import reload
import matplotlib.path as mpath
import glob
import time
import prophy_fxns as pf



yr = 1950
pftv = ['dia','mix','coc','pic','pha','fix']

for yr in range(1950,2020):
    
    for x1 in range(80,170,10):
        for y1 in range(70,160,10):

            for pft in pftv:

                LoP = f'/gpfs/data/greenocean/software/runs/TOM12_TJ_LA02//ORCA2_1m_{yr}0101_{yr}1231_LoP_T.nc'
                diad = f'/gpfs/data/greenocean/software/runs/TOM12_TJ_LA02//ORCA2_1m_{yr}0101_{yr}1231_diad_T.nc'
                ptrc = f'/gpfs/data/greenocean/software/runs/TOM12_TJ_LA02//ORCA2_1m_{yr}0101_{yr}1231_ptrc_T.nc'
                grid = f'/gpfs/data/greenocean/software/runs/TOM12_TJ_LA02//ORCA2_1m_{yr}0101_{yr}1231_grid_T.nc'
                savestr = f'/gpfs/data/greenocean/software/runs/TOM12_TJ_LA02//ORCA2_1m_{yr}0101_{yr}1231_prophy_{pft}_x{x1}_y{y1}_T.nc'
                
                print(savestr)
                t1 = time.time()
                pf.make_nc(LoP, diad, ptrc, grid, savestr, pft, x1, y1)
                t2 = time.time()
                print(t2-t1)