import xarray as xr
import numpy as np

pftv = ['dia','mix','coc','pic','pha','fix']
# #pftv = ['dia']




ex = True

yrst = 1966
yren = 2023

if ex:

    for yr in range(yrst,yren):
        ar = np.zeros([12, 31, 149, 182])
        print(yr)
        try:
            for pft in pftv:
                #print(pft)
                ss1 = f'/gpfs/data/greenocean/software/runs/TOM12_TJ_LA02//ORCA2_1m_{yr}0101_{yr}1231_prophy_{pft}_ATL_T.nc'
                print(ss1)
                for x1 in range(80,170,10):
                    for y1 in range(70,160,10):

                        ss = f'/gpfs/data/greenocean/software/runs/TOM12_TJ_LA02//ORCA2_1m_{yr}0101_{yr}1231_prophy_{pft}_x{x1}_y{y1}_T.nc'
                        w = xr.open_dataset(ss)
                        try:
                            ar[:,:,y1:y1+10,x1:x1+10] = w['prophy'][:,:,y1:y1+10,x1:x1+10]
                        except:
                            print(f'no for x{x1}, y{y1}')
                w['prophy'].values = ar
                w = w.rename({"prophy": pft})
                w.to_netcdf(ss1)
        except:
            print(f'no for {yr}')

                          
                          
