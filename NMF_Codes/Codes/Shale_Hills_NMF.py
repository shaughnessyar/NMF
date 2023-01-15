#load packages
import pandas as pd
from sklearn.decomposition import NMF
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

pd.options.mode.chained_assignment = None

#normalized data from pre-process
data_norm = pd.read_csv('shale_hills_norm_data.csv', header=0, index_col=None)
#normalized bootstrapped data from pre-process
data_synthetic = pd.read_csv('shale_hills_boot_norm_data.csv', header=0, index_col=None)

#set up the model
def run_model(start = None):
    #number of components from PCA (explains 90% variation)
    model = NMF(n_components=2, init='random',
            solver = 'cd', random_state=start+1,
            max_iter = 100000,  tol = 1e-4)
    mod = model.fit(data_synthetic)
    W = mod.transform(data_norm)
    H = mod.components_
    data_col_names = list(data_norm.columns.values)
    result = pd.DataFrame(W, columns=['comp1', 'comp2'])
    result['tot'] = result['comp1']+ result['comp2']
    #filter results that dont sum to unity
    result = result[result['tot'] > 0.95]
    result = result[result['tot'] < 1.05]
    result['sample'] = result.index + 1

    em = pd.DataFrame(H, columns=data_col_names)

    #define split rule from 10 initial decompositions
    index_max = np.argmax(em['Cl_SO4'])

    if index_max == 1:
        result['rain'] = result['comp2']
        result['rock'] = result['comp1']
    else:
        result['rain'] = result['comp1']
        result['rock'] = result['comp2']

    #save results
    result['run'] = start
    cols = ['rock','rain', 'sample', 'run']
    result = result[cols]
    result['Ca_mod'] = result['rain'] * em.loc[index_max,'Ca_SO4'] + result['rock'] * em.loc[1-index_max,'Ca_SO4']
    result['Mg_mod'] = result['rain'] * em.loc[index_max,'Mg_SO4'] + result['rock'] * em.loc[1-index_max,'Mg_SO4']
    result['Na_mod'] = result['rain'] * em.loc[index_max,'Na_SO4'] + result['rock'] * em.loc[1-index_max,'Na_SO4']
    result['K_mod'] = result['rain'] * em.loc[index_max,'K_SO4'] + result['rock'] * em.loc[1-index_max,'K_SO4']
    result['Cl_mod'] = result['rain'] * em.loc[index_max,'Cl_SO4'] + result['rock'] * em.loc[1-index_max,'Cl_SO4']
    result['Ca_SO4_rock'] = em.loc[1-index_max,'Ca_SO4']
    result['Mg_SO4_rock'] = em.loc[1-index_max,'Mg_SO4']
    result['Na_SO4_rock'] = em.loc[1-index_max,'Na_SO4']
    result['K_SO4_rock'] = em.loc[1-index_max,'K_SO4']
    result['Cl_SO4_rock'] = em.loc[1-index_max,'Cl_SO4']
    result['Ca_SO4_rain'] = em.loc[index_max,'Ca_SO4']
    result['Mg_SO4_rain'] = em.loc[index_max,'Mg_SO4']
    result['Na_SO4_rain'] = em.loc[index_max,'Na_SO4']
    result['K_SO4_rain'] = em.loc[index_max,'K_SO4']
    result['Cl_SO4_rain'] = em.loc[index_max,'Cl_SO4']

    return result

#run the model in parallel
final = pd.DataFrame()
pool = ThreadPoolExecutor(5)
futures = []
for x in range(20000):
    futures.append(pool.submit(run_model, x))

counter = 1
for x in as_completed(futures):
    final = pd.concat([final, x.result()])
    print('model run: {}'.format(counter))
    counter = counter + 1

#write results to csv
final.to_csv('shale_hills_NMF_output.csv', index=False)
print('Done.')
