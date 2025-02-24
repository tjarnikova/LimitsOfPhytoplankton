import xarray as xr
import glob
import numpy as np

ex = True

nam = 'LA02'

def make_yearlist(yrst, yrend, typ = 'PPINT'):
    yrs = np.arange(yrst,yrend+1,1)
    ylist = []
    
    for yr in (yrs):
        tyr = glob.glob(f'/gpfs/data/greenocean/software/runs/TOM12_TJ_{nam}//ORCA2_1m_{yr}0101_{yr}1231_{typ}_T.nc')
        ylist.append(tyr)
        
    return ylist

##atl 
atl = xr.open_dataset('/gpfs/home/mep22dku/scratch/AMOC-PLANKTOM/data/meshmask_with_Atl.nc')

(atl)

area_broad = np.zeros([1,31,149,182])

for i in range(0,31):
    
    area_broad[0,i,:,:] = atl.tmask[0,i,:,:]*atl.e1t[0,:,:]*atl.e2t[0,:,:]

atl['NAT_area'] = atl.NAT * area_broad
atl['NAL_area'] = atl.NAL * area_broad
atl['NAM_area'] = atl.NAM * area_broad
atl['NAH_area'] = atl.NAH * area_broad
atl['ATL_area'] = atl.ATL * area_broad

atl = atl.squeeze(dim="t")
atl = atl.rename({'z': 'deptht'})


yrst = 1951; yrend = 2023

if ex:
    
    for yr in range(yrst,yrend):
        try:

            yrst = yr; yrend = yr

            ylist = make_yearlist(yrst, yrend)
            ppint = xr.open_mfdataset(ylist)
            ylist = make_yearlist(yrst, yrend, typ = 'diad')
            diad = xr.open_mfdataset(ylist)
            ylist = make_yearlist(yrst, yrend, typ = 'ptrc')
            ptrc = xr.open_mfdataset(ylist)

            msks = ['ATL', 'NAT','NAL','NAM','NAH']
            tdats = [ptrc, diad, ppint]
            # tdatns = ['ptrc', 'diad', 'ppint']
            # for i in range(0,1):
            #     tdat = tdats[i]
            #     tdatn = tdatns[i]
            for mask in msks:
                tdatn = 'ptrc'; tdat = ptrc
                q = ['O2','PIIC','DOC','CaCO3','ARA','POC','GOC','BSi','GON','time_centered_bounds','time_counter_bounds']
                tdat = tdat.drop_vars(q)
                tdatnam = f'{tdatn}_'; masknam = f'{mask}_area'
                savenam = f'./data/{nam}-{tdatnam}{yrst}-{mask}.nc'
                print(savenam)
                ds = tdat.weighted(atl[masknam]).mean(dim = ['x','y'])
                ds.to_netcdf(savenam)
                #print(ds)

                tdatn = 'diad'; tdat = diad
                #print(list(tdat.variables))
                q2 = [
                 'time_counter_bounds','CARBTRP','CAPITRP','ALKTRP','GRAMIC',
                 'GRAMES','GRAMAC','PPTDOC','Detrit','Carniv',
                 'Herbiv','GRAMICPHY','GRAPTEPHY','GRAMESPHY','GRAGELPHY',
                 'GRAMACPHY','nitrfix','denitr','DELO2','vsink','sinksil','discarb','ExpCO3','ExpARA',
                 'GRAGEL','GRAPTE','proara','prococ','lim2mmfe_dia','lim2mmfe_mix','lim2mmfe_coc','lim2mmfe_pic',
                 'lim2mmfe_pha','lim2mmfe_fix','PICflx','Oflx','time_centered_bounds','time_counter_bounds']
                tdat = tdat.drop_vars(q2)
                tdatnam = f'{tdatn}_'; masknam = f'{mask}_area'
                savenam = f'./data/{nam}-{tdatnam}{yrst}-{mask}.nc'
                print(savenam)
                ds = tdat.weighted(atl[masknam]).mean(dim = ['x','y'])            
                ds.to_netcdf(savenam)

                tdatn = 'ppint'; tdat = ppint
                tdatnam = f'{tdatn}_'; masknam = f'{mask}_area'
                savenam = f'./data/{nam}-{tdatnam}{yrst}-{mask}.nc'
                print(savenam)
                ds = tdat.weighted(atl[masknam]).mean(dim = ['x','y'])            
                ds.to_netcdf(savenam)
        except:
            print(f'yr {yr} problem')