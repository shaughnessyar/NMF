#load packages
import pandas as pd
from sklearn.decomposition import NMF
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

pd.options.mode.chained_assignment = None

#normalized data from pre-process
data_norm = pd.DataFrame.from_csv('susquehanna_river_norm_data.csv', header=0, index_col=None)
#normalized bootstrapped data from pre-process
data_synthetic = pd.DataFrame.from_csv('susquehanna_river_boot_norm_data.csv', header=0, index_col=None)

#set up the model
def run_model(start = None):
    try:
        #number of components from PCA (explains 90% variation)
        model = NMF(n_components=3, init='random',
                solver = 'cd', random_state=start+1,
                max_iter = 100000,  tol = 1e-4)
        mod = model.fit(data_synthetic)
        W = mod.transform(data_norm)
        H = mod.components_
        data_col_names = list(data_norm.columns.values)
        result = pd.DataFrame(W, columns=['comp1', 'comp2', 'comp3'])
        result['tot'] = result['comp1']+ result['comp2']+ result['comp3']
        result = result[result['tot'] > 0.95]
        result = result[result['tot'] < 1.05]
        result['sample'] = result.index + 1
        seed = start + 1

        em = pd.DataFrame(H, columns=data_col_names)

        #define split rule from 10 initial decompositions
        index_max_cl = np.argmax(em['Cl_SO4'])
        index_max_no3 = np.argmax(em['NO3_SO4'])
        index_rock = 3 - index_max_cl - index_max_no3

        if index_max_cl == 1 and index_max_no3 == 2:
            result['fert'] = result['comp3']
            result['rain'] = result['comp2']
            result['rock'] = result['comp1']
        elif index_max_cl == 0 and index_max_no3 == 1:
            result['fert'] = result['comp2']
            result['rain'] = result['comp1']
            result['rock'] = result['comp3']
        elif index_max_cl == 0 and index_max_no3 == 2:
            result['fert'] = result['comp3']
            result['rain'] = result['comp1']
            result['rock'] = result['comp2']
        elif index_max_cl == 2 and index_max_no3 == 1:
            result['fert'] = result['comp2']
            result['rain'] = result['comp3']
            result['rock'] = result['comp1']
        elif index_max_cl == 2 and index_max_no3 == 0:
            result['fert'] = result['comp1']
            result['rain'] = result['comp3']
            result['rock'] = result['comp2']
        else:
            result['fert'] = result['comp1']
            result['rain'] = result['comp2']
            result['rock'] = result['comp3']

        #save results
        result['run'] = start
        cols = ['rock','rain', 'fert', 'sample', 'run']
        result = result[cols]

        result['Ca_mod'] = result['rain'] * em.loc[index_max_cl,'Ca_SO4'] +\
         result['rock'] * em.loc[index_rock,'Ca_SO4'] +\
         result['fert'] * em.loc[index_max_no3,'Ca_SO4']

        result['Mg_mod'] = result['rain'] * em.loc[index_max_cl,'Mg_SO4'] +\
         result['rock'] * em.loc[index_rock,'Mg_SO4'] +\
         result['fert'] * em.loc[index_max_no3,'Mg_SO4']

        result['Na_mod'] = result['rain'] * em.loc[index_max_cl,'Na_SO4'] +\
         result['rock'] * em.loc[index_rock,'Na_SO4'] +\
         result['fert'] * em.loc[index_max_no3,'Na_SO4']

        result['K_mod'] = result['rain'] * em.loc[index_max_cl,'K_SO4'] +\
         result['rock'] * em.loc[index_rock,'K_SO4'] +\
         result['fert'] * em.loc[index_max_no3,'K_SO4']

        result['Cl_mod'] = result['rain'] * em.loc[index_max_cl,'Cl_SO4'] +\
         result['rock'] * em.loc[index_rock,'Cl_SO4'] +\
         result['fert'] * em.loc[index_max_no3,'Cl_SO4']

        result['NO3_mod'] = result['rain'] * em.loc[index_max_cl,'NO3_SO4'] +\
         result['rock'] * em.loc[index_rock,'NO3_SO4'] +\
         result['fert'] * em.loc[index_max_no3,'NO3_SO4']


        result['Ca_SO4_rock'] = em.loc[index_rock,'Ca_SO4']
        result['Mg_SO4_rock'] = em.loc[index_rock,'Mg_SO4']
        result['Na_SO4_rock'] = em.loc[index_rock,'Na_SO4']
        result['K_SO4_rock'] = em.loc[index_rock,'K_SO4']
        result['Cl_SO4_rock'] = em.loc[index_rock,'Cl_SO4']
        result['NO3_SO4_rock'] = em.loc[index_rock,'NO3_SO4']

        result['Ca_SO4_rain'] = em.loc[index_max_cl,'Ca_SO4']
        result['Mg_SO4_rain'] = em.loc[index_max_cl,'Mg_SO4']
        result['Na_SO4_rain'] = em.loc[index_max_cl,'Na_SO4']
        result['K_SO4_rain'] = em.loc[index_max_cl,'K_SO4']
        result['Cl_SO4_rain'] = em.loc[index_max_cl,'Cl_SO4']
        result['NO3_SO4_rain'] = em.loc[index_max_cl,'NO3_SO4']

        result['Ca_SO4_fert'] = em.loc[index_max_no3,'Ca_SO4']
        result['Mg_SO4_fert'] = em.loc[index_max_no3,'Mg_SO4']
        result['Na_SO4_fert'] = em.loc[index_max_no3,'Na_SO4']
        result['K_SO4_fert'] = em.loc[index_max_no3,'K_SO4']
        result['Cl_SO4_fert'] = em.loc[index_max_no3,'Cl_SO4']
        result['NO3_SO4_fert'] = em.loc[index_max_no3,'NO3_SO4']

        return result

    except:
        #error if none of the delineation rules are followed
        print("error in seed: {}".format(seed))

final = pd.DataFrame()
pool = ThreadPoolExecutor(30)
futures = []
for x in range(10000):
    futures.append(pool.submit(run_model, x))

counter = 1
for x in as_completed(futures):
    final = pd.concat([final, x.result()])
    print('model run: {}'.format(counter))
    counter = counter + 1

final.to_csv('susquehanna_river_NMF_output.csv', index=False)
print('Done.')
