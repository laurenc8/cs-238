from .random_2 import random
from gerrychain.partition import Partition
import pandas as pd

def always_accept(partition: Partition) -> bool:
    return True

def community_comparison(partition: Partition) -> bool:
    df = pd.DataFrame.from_dict(partition.graph.nodes._nodes, orient='index')
    assign = pd.DataFrame.from_dict(partition.assignment.mapping, orient='index')
    # print('assign', assign)
    final_df = df.merge(assign, left_index=True, right_index=True)
    # print(final_df)
    return True; #lauren_function(final_df) > 1;

def cut_edge_accept(partition: Partition) -> bool:
    """Always accepts the flip if the number of cut_edges increases.
    Otherwise, uses the Metropolis criterion to decide.

    :param partition: The current partition to accept a flip from.
    :return: True if accepted, False to remain in place

    """
    bound = 1.0

    if partition.parent is not None:
        bound = min(1, len(partition.parent["cut_edges"]) / len(partition["cut_edges"]))

    return random.random() < bound
