import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import json
from gerrychain import (GeographicPartition, Partition, Graph, MarkovChain,
                        proposals, updaters, constraints, accept, Election)

df_coi = gpd.read_file('shp_data/coi-products/Michigan/shapefile_summary/MI_20211207_phase_C_summary/MI_20211207_phase_C_summary.shp')
print(df_coi.head())
# print(len(df))
# print(df.columns)
# df.plot("cluster", legend=True)

mi_precinct = gpd.read_file('shp_data/MI/mi16_results.shp')
print(mi_precinct.columns)

df_coi2 = df_coi.to_crs("epsg:6493") #(epsg=6493, inplace=True, allow_override=True)

how = 'left'
pred = 'within'
mi_coi_precinct = mi_precinct.sjoin(df_coi2, how=how, predicate=pred)
# mi_coi_precinct.to_csv(f'COMBINED_{how}_{pred}.csv')

print(mi_coi_precinct.head())
print(mi_coi_precinct.index)
mi_coi_precinct['ind'] = mi_coi_precinct.index
print(mi_coi_precinct.drop_duplicates(subset=['ind']))

graph = Graph.from_geodataframe(mi_coi_precinct)


elections = [
    Election("SEN18", {"Democratic": "SEN18D", "Republican": "SEN18R"})
]

# Population updater, for computing how close to equality the district
# populations are. "TOTPOP" is the population column from our shapefile.
my_updaters = {"population": updaters.Tally("TOTPOP", alias="population")}

# Election updaters, for computing election results using the vote totals
# from our shapefile.
election_updaters = {election.name: election for election in elections}
my_updaters.update(election_updaters)

assignment = {n : graph.nodes[n]["CD"] for n in graph.nodes}
initial_partition = Partition(graph, assignment=assignment, updaters=my_updaters)

initial_partition.plot(graph, figsize=(10, 10), cmap="tab20")
plt.axis('off')
plt.show()

# The ReCom proposal needs to know the ideal population for the districts so that
# we can improve speed by bailing early on unbalanced partitions.

ideal_population = sum(initial_partition["population"].values()) / len(initial_partition)
# We use functools.partial to bind the extra parameters (pop_col, pop_target, epsilon, node_repeats)
# of the recom proposal.
proposal = partial(recom,
                   pop_col="TOTPOP",
                   pop_target=ideal_population,
                   epsilon=0.02,
                   node_repeats=2
                  )

compactness_bound = constraints.UpperBound(
    lambda p: len(p["cut_edges"]),
    2*len(initial_partition["cut_edges"])
)

pop_constraint = constraints.within_percent_of_ideal_population(initial_partition, 0.02)

chain = MarkovChain(
    proposal=proposal,
    constraints=[
        pop_constraint,
        compactness_bound
    ],
    accept=accept.community_comparison,
    initial_state=initial_partition,
    total_steps=1000
)
print('made chain')

ensemble_df = pd.DataFrame(columns=["nodes"] + list(range(1000)))
first_time = True
for i, partition in enumerate(chain):
  part_series = partition.assignment.to_series().sort_index()
  ensemble_df[i] = list(part_series)
  if first_time:
     ensemble_df["nodes"] = list(part_series.index)
     print(ensemble_df["nodes"])
     first_time = False


# # michigan_cd = pd.read_json('../docs/user/michigan_dualgraph.json')
# with open('../docs/user/michigan_dualgraph.json') as json_data:
#     data = json.load(json_data)
#     print(data.keys())
#     # print('specific column', data['nodes']) #idk what adjacency is
#     dfn = pd.DataFrame(data['nodes'])
#     print(dfn.columns)
#
# # print(michigan_cd)
#
# # cities_with_country = cities.sjoin(countries, how="inner", predicate='intersects')
#
# # plt.show()
#

