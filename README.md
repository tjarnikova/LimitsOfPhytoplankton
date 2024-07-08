- an experimental routine to calculate nutrient limitation in PlankTOM12 models
- as of 2024-07 iron subroutine not implemented

help for main subroutine:

    written by TJŠJ at UEA, 2024, T.Jarnikova [a] uea.ac.uk
    based on /gpfs/home/avd22gnu/scratch/modelTest/RIV12/NEMO/TOP_SRC/PlankTOM/bgcpro.F90 (by OA and ET) 
    
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
