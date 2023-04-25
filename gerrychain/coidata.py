import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df_coi = gpd.read_file('shp_data/coi-products/Michigan/shapefile_summary/MI_20211207_phase_C_summary/MI_20211207_phase_C_summary.shp')

mi_precinct = gpd.read_file('shp_data/MI/mi16_results.shp')

df_coi2 = df_coi.to_crs("epsg:6493") #(epsg=6493, inplace=True, allow_override=True)

how = 'left'
pred = 'within'
mi_coi_precinct = mi_precinct.sjoin(df_coi2, how=how, predicate=pred)

mi_coi_precinct['ind'] = mi_coi_precinct.index
mi_coi_precinct3 = mi_coi_precinct.drop_duplicates(subset=['ind'])
# mi_coi_precinct3.to_csv(f'COMBINED_final.csv')

cond_entr = pd.read_csv('vendor/michigan_ensemble.csv')
print(cond_entr['999'])
mi_coi_precinct3['cond_entr'] = cond_entr['999']

base = mi_coi_precinct3.plot(column='cluster', cmap="Pastel1", zorder=1)

just_CDs = mi_coi_precinct3.dissolve(by='cond_entr', aggfunc='sum')

print('just cds', just_CDs.head())
print(just_CDs.columns)

just_CDs.plot(ax=base, cmap="Pastel2", zorder=2, facecolor="none", edgecolor="black")
# mi_coi_precinct3.plot(column='cluster', cmap="Pastel1", facecolor="none") #, edgecolor="black"
plt.
plt.axis("off")
plt.show()