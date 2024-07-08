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
import LimitsOfPhytoplankton as LoP



trcsmsPath = '/gpfs/home/mep22dku/scratch/ModelRuns/TOM12_TJ_R4A0/namelist.trc.sms'
modelName =  'TOM12_TJ_R4A1'
year = 2023
ModelDirectory = '/gpfs/data/greenocean/software/runs/'
whereToSave = '/gpfs/home/mep22dku/scratch/LimitsOfPhytoplankton/data/'
verbose = True
dlim = 1 #just surface

#DIA MIX CO    PIC     PHA     FIX 
# pPFT = 'DIA'
# LoP.GetLimitsOfPhytoplankton(trcsmsPath,modelName,year,pPFT, verbose = True, dlim = 1)
# pPFT = 'MIX'
# LoP.GetLimitsOfPhytoplankton(trcsmsPath,modelName,year,pPFT, verbose = True, dlim = 1)
# pPFT = 'COC'
# LoP.GetLimitsOfPhytoplankton(trcsmsPath,modelName,year,pPFT, verbose = True, dlim = 1)
# pPFT = 'PIC'
# LoP.GetLimitsOfPhytoplankton(trcsmsPath,modelName,year,pPFT, verbose = True, dlim = 1)
# pPFT = 'PHA'
# LoP.GetLimitsOfPhytoplankton(trcsmsPath,modelName,year,pPFT, verbose = True, dlim = 1)
pPFT = 'FIX'
LoP.GetLimitsOfPhytoplankton(trcsmsPath,modelName,year,pPFT, verbose = True, dlim = 1)