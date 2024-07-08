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



def findInTrcSms(filename, variable, lon = 6, verbose = True):
    
    #for finding variables in namelist.trc.sms and returning them as an array
    w5 = np.nan
    with open(filename, 'r') as file:
        for line in file:
            ## find and parse the variables
            if variable in line:
                w = line.strip()
                w1 = ''.join(w.split())
                w2 = w1.split('=')
                w3 = w2[1].split(',')
                w4 = w3[0:lon]
                w5 = np.array(w4).astype(float)
                if verbose: 
                    print(w)
                    print(w5)
    return w5
                        

def getParsFromTrcSms(namtrc, verbose = True):
    

    rn_kmpphy = findInTrcSms(namtrc, 'rn_kmpphy', verbose = False)
    rn_kmnphy = findInTrcSms(namtrc, 'rn_kmnphy', verbose = False)
    rn_nutthe = findInTrcSms(namtrc, 'rn_nutthe',lon = 1, verbose = False)
    rn_sildia = findInTrcSms(namtrc, 'rn_sildia',lon = 1, verbose = False)
    rn_munfix = findInTrcSms(namtrc, 'rn_munfix',lon = 1, verbose = False)
    
    if verbose:
        print(f'rn_kmpphy: {rn_kmpphy} (nitrogen half saturation concentrat.)')
        print(f'rn_kmnphy: {rn_kmnphy} (phosphate half saturation concentration)')
        print(f'rn_nutthe: {rn_nutthe}')
        print(f'rn_sildia: {rn_sildia}')    
        print(f'rn_sildia: {rn_munfix}') 

    return rn_kmpphy, rn_kmnphy, rn_nutthe, rn_sildia, rn_munfix 


def get_lim(pPFT,jppo4,jpsil,jpdin, rn_kmpphy, rn_kmnphy, rn_nutthe, rn_sildia, rn_munfix, verbose = False):
    
    mapping = {
        "DIA": 0,
        "MIX": 1,
        "COC": 2,
        "PIC": 3,
        "PHA": 4,
        "FIX": 5
    }

    rn_kmpphy = rn_kmpphy[mapping[pPFT]]
    rn_kmnphy = rn_kmnphy[mapping[pPFT]]
    rn_nutthe = rn_nutthe[0]    
    rn_sildia = rn_sildia[0]    
    rn_munfix = rn_munfix[0]
        
    if verbose:
        print(f'for {pPFT} we have the following parameters')
        print(f'rn_kmpphy: {rn_kmpphy} (nitrogen half saturation concentrat.)')
        print(f'rn_kmnphy: {rn_kmnphy} (phosphate half saturation concentration)')

        print('----')
        print(f'we are furthermore using the following constants')
        print(f'rn_nutthe: {rn_nutthe}')
        print(f'rn_sildia: {rn_sildia}')

    xlim5_sil = 1 ## silica limita
    xlim_fer = 1 #we don't fully understand iron, iron model not currently in
    
    limnut = -99 #(1 = NO3, 2 = Si, 3 = PO4, 4 = Fe)
    xlim_phyt = -99 
    
    xlim4_po4 = (jppo4 - rn_kmpphy * rn_nutthe) / ((jppo4) + rn_kmpphy * (1 - rn_nutthe))
    
    if pPFT == 'DIA':
        
        xlim5_sil = (jpsil - rn_sildia * rn_nutthe) / (jpsil + rn_sildia * (1 - rn_nutthe))
        
    xlim6_din = (jpdin - rn_kmnphy * rn_nutthe) / (jpdin + rn_kmnphy * (1 - rn_nutthe))
    
    if pPFT == 'FIX':
        
        dinlim = (jpdin - rn_kmnphy * rn_nutthe) / (jpdin + rn_kmnphy * (1 - rn_nutthe))
        xlim6_din = dinlim +rn_munfix*(1.-dinlim)
        

    xlim_phyt = np.min([xlim4_po4,xlim5_sil,xlim6_din,xlim_fer])
    
    #(1 = NO3, 2 = Si, 3 = PO4, 4 = Fe)

    if xlim_phyt == xlim6_din:
        limnut = 1
    if xlim_phyt == xlim5_sil:
        limnut = 2
    if xlim_phyt == xlim4_po4:
        limnut = 3
    if xlim_phyt == xlim_fer:
        limnut = 4

    if verbose:
        
        print('---')
        try:
            print(f'NO3 limitation {xlim6_din.values}')
        except:
            print(f'NO3 limitation {xlim6_din}') 
        try:
            print(f'Si limitation {xlim5_sil.values}') 
        except:
            print(f'Si limitation {xlim5_sil}') 
        try:
            print(f'PO4 limitation {xlim4_po4.values}')  
        except:
            print(f'PO4 limitation {xlim4_po4}')  
        try:
            print(f'Fer limitation {xlim_fer.values}')
        except:
            print(f'Fer limitation {xlim_fer}')
        print('--')
        print(f'limiting nutrient is: {limnut} with value of {xlim_phyt}')
        print('(1 = NO3, 2 = Si, 3 = PO4, 4 = Fe)')
        
    return limnut, xlim_phyt

def GetLimitsOfPhytoplankton(trcsmsPath,modelName,year,pPFT,ModelDirectory = '/gpfs/data/greenocean/software/runs/', \
                             whereToSave = '/gpfs/home/mep22dku/scratch/LimitsOfPhytoplankton/data/', verbose = False, dlim = 23):
    
    '''
    
    written by TJŠJ at UEA, 2024, T.Jarnikova@uea.ac.uk
    based on RIV12/NEMO/TOP_SRC/PlankTOM/bgcpro.F90, written by ET
    
    calculates limiting nutrient from ptrc outputs for a given model, year, phytoplankton functional type, and namelist.trc.sms. 
    saves as: {WhereToSave}/{modelName}_y{year}_{pPFT}_LoP.nc
    saves both limiting nutrient (1 = NO3, 2 = Si, 3 = PO4, 4 = Fe) and value of nutrient limitation (0-1)

    arguments:
    trcsmsPath 
        path to namelist.trc.sms. eg '/gpfs/home/mep22dku/scratch/ModelRuns/TOM12_TJ_R4A0/namelist.trc.sms'
    modelName
        name of model, eg TOM12_TJ_RVA0
    year
        year to run for, eg 1955 
    pPFT
        functional group, one of DIA MIX COC	PIC	PHA	FIX	
    ModelDirectory = '/gpfs/data/greenocean/software/runs/'
        where model is found, default shown above;
    whereToSave = '/gpfs/home/mep22dku/scratch/LimitsOfPhytoplankton/data/', 
        where model is found, default shown above;
    verbose = False, 
        if this is true the script outputs various facts about what it's doing
    dlim = 23
        depth level to calculate to - this is an expensive routine, by default it goes up to but not including depth level 23
        (python indexing, first level is 0. by default last included level is approx 1000 m)
    
    '''
    
    t1 = time.time()
    ## get and open ptrc
    w = xr.open_dataset(glob.glob(f'{ModelDirectory}{modelName}/*{year}*ptrc*nc')[0])
    nav_lat = w.nav_lat
    nav_lon = w.nav_lon
    deptht = w.deptht
    time_counter = w.time_counter
    
    #get vals out as array
    NO3 = w.NO3.values
    Si = w.Si.values
    PO4 = w.PO4.values
    
    tmask = xr.open_dataset('/gpfs/data/greenocean/software/resources/regrid/mesh_mask3_6.nc')
    tmesh = tmask.tmask.values 
    
    limitNut = np.zeros([12,31,149,182])
    limitVal = np.zeros([12,31,149,182])
    
    savenam = f'{whereToSave}/{modelName}_y{year}_{pPFT}_LoP_d0-{dlim-1}.nc'
    if verbose:
        print(f'making {savenam}')
        
    rn_kmpphy, rn_kmnphy, rn_nutthe, rn_sildia, rn_munfix = getParsFromTrcSms(trcsmsPath, verbose = True) 
    

    for d in range(0,dlim): #do 
        for y in range(0,149): #149
            if verbose:
                print(f'y {y}')
            
            for x in range(0,182): #182

                if tmesh[0,d,y,x] == 0:
                    pass
                else:
                    for t in range(0,12):

                        jpdin = NO3[t,d,y,x]
                        jpsil = Si[t,d,y,x]
                        jppo4 = PO4[t,d,y,x]
                        limnut, xlim_phyt = get_lim(pPFT,jppo4,jpsil,jpdin, rn_kmpphy, rn_kmnphy, rn_nutthe, rn_sildia, rn_munfix, verbose = False)
                        limitNut[t,d,y,x] = limnut
                        limitVal[t,d,y,x] = xlim_phyt
                        

    ### save as .nc    
    data_vars = {'limitNut':(['time_counter', 'deptht', 'y', 'x'], limitNut,
    {'units': 'dimensionless',
    'long_name':'limiting nutrient (1 = NO3, 2 = Si, 3 = PO4, 4 = Fe) '}),
                 'limitVal':(['time_counter', 'deptht', 'y', 'x'], limitVal,
    {'units': 'dimensionless',
    'long_name':'value of nutrient limitation, 0-1'}),
    }
    # define coordinates
    coords = {'time_counter': (['time_counter'], time_counter),
    'nav_lat': (['y','x'], nav_lat),
    'nav_lon': (['y','x'], nav_lon),
    'deptht': (['deptht'], deptht)}
    # define global attributes
    attrs = {'made in':'/LimitsOfPhytoplankton/LimitsOfPhytoplankton.py',
    'desc': f'calculated to depth level {dlim}'
    }
    ds = xr.Dataset(data_vars=data_vars,
    coords=coords,
    attrs=attrs)
    ds.to_netcdf(savenam)


    t2 = time.time()
    if verbose:
        print(f'seconds taken: {t2-t1}')
#     return w
    return
    
