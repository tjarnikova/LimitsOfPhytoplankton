import xarray as xr
import numpy as np
import time

def get_tgfunc(tsn,pft, verbose = False):

    rn_mutpft =     np.array([18.80   ,  22.00  ,   31.60  , 31.60  ,  23.60  ,  33.20  , \
                              23.20  ,  34.00  ,  20.40  ,  24.80  ,  15.60  ,  27.60  ,])
    rn_mudpft =     np.array([20.0    ,  20.0   ,   20.0   , 20.0   ,  18.8   ,  20.0   , \
                              17.2   ,  20.0   ,   7.4   ,  11.2   ,  13.0   ,  8.2    ,])
    
    pftv = ['dia','mix','coc','pic','pha','fix']
    index_of_pft= pftv.index(pft)
    
    tgfunc = np.exp(-1.*(tsn-rn_mutpft[index_of_pft])**2./rn_mudpft[index_of_pft]**2.)

    
    if pft == 'coc':
        ztemp = 10.
        ztmax = (1./5. + 4./5.*max(tsn,-1.8)/(ztemp))*tgfunc
        tgfunc = min(ztmax,tgfunc)
        
    if verbose:
        print(tgfunc)
        
    return tgfunc


def get_prophy(tgfunc, pft, xlimpft, xlim8, conc_pft):
    
    rfact = 5760.0000000000000 #(tracer time step)
    rjjss = 60*60*24 #secondsday
    
    pftv = ['dia','mix','coc','pic','pha','fix']
    index_of_pft= pftv.index(pft)
    
    rn_mumpft =    np.array([ 1.3    ,  1.1    ,  1.0    ,  0.8    ,  1.4    ,  0.2    ,])
    rn_resphy =     np.array([0.12   ,  0.15   ,  0.15   ,  0.15   ,  0.15   ,  0.15   ,])
    
    pcmax = rn_mumpft[index_of_pft]*(1.+rn_resphy[index_of_pft])/rjjss 
    pctnut=pcmax * xlimpft * tgfunc
    pcphot = pctnut * xlim8
    prophy = pcphot * conc_pft
    
    return prophy

def get_datasets(LoP, diad, ptrc, grid):

    ptrcd = xr.open_dataset(ptrc)
    LoPd = xr.open_dataset(LoP)
    gridd = xr.open_dataset(grid)
    diadd = xr.open_dataset(diad)
    
    return ptrcd, LoPd, gridd, diadd
    
def get_prophytot(x, y, z, t, pft, ptrcd, LoPd, gridd, diadd):
    
    tsn = gridd.votemper[t,z,y,x]
    tgfunc = get_tgfunc(tsn,pft, verbose = False)
    tLV = f'LV_{pft}'
    xlimpft = LoPd[tLV][t,z,y,x]
    
    tlim8 = f'lim8light_{pft}'
    xlim8 = diadd[tlim8][t,z,y,x]
    
    PFT = pft.upper()
    conc_pft = ptrcd[PFT][t,z,y,x]
    
    prophy = get_prophy(tgfunc, pft, xlimpft, xlim8, conc_pft)
    prophy = prophy * 1e3 # mol/L to mol/m3
    
    return prophy

def make_nc(LoP, diad, ptrc, grid, savestr, pft, x1, y1):
    
    #pftv = ['dia','mix','coc','pic','pha','fix']
    ptrcd, LoPd, gridd, diadd = get_datasets(LoP, diad, ptrc, grid)
    
    # for t in range(0,12):
    #     for x in range(0,182):
    #         for y in range(0,149):
    #             for z in range(0,31):
    
    tsn = gridd.votemper.values
    prophyar = np.zeros_like(tsn)
    gridd['prophy'] = gridd.votemper.copy()
    
    tmesh = xr.open_dataset('/gpfs/data/greenocean/software/resources/regrid/mesh_mask3_6.nc')

    ## for natl only
    for t in range(0,12):
        print(t)
        t1 = time.time()
        
        xma = min(x1+10,182)
        yma = min(y1+10,149)
        
        for x in range(x1,xma): #80,160
            for y in range(y1,yma): #natl #70,130
                for z in range(0,15):
                    # for pft in pftv:
                    if tmesh.tmask[0,z,y,x] == 0:
                        pass
                    else:
                        prophyar[t,z,y,x] = get_prophytot(x, y, z, t, pft, ptrcd, LoPd, gridd, diadd)
        t2 = time.time()
        print(t2-t1)

    gridd['prophy'].values = prophyar
    w_sel = gridd['prophy']
    w_sel.to_netcdf(savestr)