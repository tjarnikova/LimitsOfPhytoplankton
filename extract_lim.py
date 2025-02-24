
year,model):
    savenam = f'/gpfs/home/mep22dku/scratch/AMOC-PLANKTOM/data/{model}_{year}_ptrc_atl.nc'
    print(savenam)

    tdi = '/gpfs/data/greenocean/software/runs/TOM12_TJ_'
    atl = xr.open_dataset('/gpfs/home/mep22dku/scratch/AMOC-PLANKTOM/data/meshmask_with_Atl_broad.nc')
    tfi = xr.open_dataset(f'{tdi}{model}/ORCA2_1m_{year}0101_{year}1231_ptrc_T.nc')

    varex = [
        "Alkalini","O2", "DIC", "PIIC", "NO3", "Si", "PO4", "Fer", "DOC", "CaCO3", "ARA", 
        "POC", "GOC", "BAC", "PRO", "PTE", "MES", "GEL", "MAC", "DIA", "MIX", 
        "COC", "PIC", "PHA", "FIX", "BSi", "GON"
    ]

    stormean = np.zeros([27,12,31,5])


    ama = ['ATL','NAT','NAL','NAM','NAH']


    w = time.time()
    for v in range(0,27):
        print(v)
        for a in range(0,5):

            aa = ama[a]
            var = varex[v]
            tdat = tfi[var].values * atl[aa].values
            tdat2 = atl['cvol'].copy() ### time dimensions dont line up
            tdat2.data = tdat
            tdat2 = tdat2.where(tdat2 !=0, np.nan)
            tdat3 = tdat2.weighted(atl['cvol']).mean(dim = ['x','y']).values
            stormean[v,:,:,a] = tdat3
    w2 = time.time()
    print(w2-w)


    times = pd.date_range(f"{year}/01/01",f"{year}/12/31",freq='MS',closed='left')

    data_vars = {'regmean':(['var','time_counter','deptht','prov'], stormean,
    {'units': 'model units',
    'long_name':''}),
    }
    # define coordinates
    coords = {'var': (['var'],varex),
            'time_counter': (['time_counter'], times),
              'deptht': (['deptht'], atl.deptht),
              'prov': (['prov'], ['ATL','NAT','NAL','NAM','NAH'])
            }
    # define global attributes
    attrs = {'made in':'/gpfs/home/mep22dku/scratch/AMOC-PLANKTOM/data/extract/natl_bio.py',
    'desc': ''
    }
    ds = xr.Dataset(data_vars=data_vars,
    coords=coords,
    attrs=attrs)
    ds.to_netcdf(savenam) 


for year in range(1940,2023):
    try:
        get_ptrc(year,'R4B0')
        #get_ptrc(year,'R4BH')
        get_ptrc(year,'RWB0')
        get_ptrc(year,'RWBH')
        #get_ptrc(year,'RVC0')
    except:
        print(f'{year} did not work')
    #get_ptrc(year,'RVD0')
_run,1960,/gpfs/home/mep22dku/scratch/ModelRuns
