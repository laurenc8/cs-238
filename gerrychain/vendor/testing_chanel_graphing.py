from gerrychain import (GeographicPartition, Partition, Graph, MarkovChain,
                        proposals, updaters, constraints, accept, Election)
from gerrychain.updaters import Tally, cut_edges
import matplotlib.pyplot as plt
from gerrychain.proposals import recom
from functools import partial
import pandas as pd
import networkx as nx
import geopandas as gpd
import numpy as np

# for partition in Record(chain, "pa-run.chain"):


# graph = Graph.from_json("../../docs/user/michigan_dualgraph.json")
df = gpd.read_file('../shp_data/MI/mi16_results.shp')
graph = Graph.from_geodataframe(df)

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
initial_partition = GeographicPartition(graph, assignment=assignment, updaters=my_updaters)

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

num_steps = 1000
chain = MarkovChain(
    proposal=proposal,
    constraints=[
        pop_constraint,
        compactness_bound
    ],
    accept=accept.always_accept,
    initial_state=initial_partition,
    total_steps=num_steps
)



ensemble_df = pd.DataFrame(columns=["nodes"] + list(range(num_steps)))
first_time = True
for i, partition in enumerate(chain):
  part_series = partition.assignment.to_series().sort_index()
  ensemble_df[i] = list(part_series)
  if first_time:
     ensemble_df["nodes"] = list(part_series.index)
     print(ensemble_df["nodes"])
     first_time = False

print("going to print to df")
ensemble_df.to_csv("../../docs/user/michigan_acceptall_1000_3.csv", index=False)

np.savetxt("community_scores_acceptall_1000_3.csv",
           chain.all_cscores,
           delimiter =", ",
           fmt ='% s')


#for partition in Record(chain, "michigan-run.chain", executable="pv", extreme=True):
#    print('partition', partition)


# This will take about 10 minutes.
# data = pandas.DataFrame(
#     sorted(partition["SEN18"].percents("Democratic"))
#     for partition in chain
# )

# fig, ax = plt.subplots(figsize=(8, 6))
#
# # Draw 50% line
# ax.axhline(0.5, color="#cccccc")
#
# # Draw boxplot
# data.boxplot(ax=ax, positions=range(len(data.columns)))
#
# # Draw initial plan's Democratic vote %s (.iloc[0] gives the first row)
# plt.plot(data.iloc[0], "ro")
#
# # Annotate
# ax.set_title("Comparing the 2011 plan to an ensemble")
# ax.set_ylabel("Democratic vote % (Senate 2012)")
# ax.set_xlabel("Sorted districts")
# ax.set_ylim(0, 1)
# ax.set_yticks([0, 0.25, 0.5, 0.75, 1])
#
# plt.show()
