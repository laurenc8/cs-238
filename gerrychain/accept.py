from .random_2 import random
from gerrychain.partition import Partition
import pandas as pd
from locality_splitting import metrics

df_coi = pd.read_csv('../COMBINED_final.csv')
df_coi = df_coi[['VTD', 'cluster']]

def always_accept(partition: Partition, old_state) -> bool:
    proposed_next_state = merge_dfs(partition)
    state = merge_dfs(old_state)
    state_scores = metrics.calculate_all_metrics(state, plan_col='CD_new', lclty_col='cluster', pop_col='TOTPOP')
    proposed_scores = metrics.calculate_all_metrics(proposed_next_state, plan_col='CD_new', lclty_col='cluster', pop_col='TOTPOP')

    return True, proposed_scores['conditional_entropy'], state_scores['conditional_entropy']

def merge_dfs(state):
    nodes = pd.DataFrame.from_dict(state.graph.nodes._nodes, orient='index')
    nodes = nodes[['VTD', 'TOTPOP']]
    assign = pd.DataFrame.from_dict(state.assignment.mapping, orient='index')
    assign['CD_new'] = assign[0]
    df = nodes.merge(assign, left_index = True, right_index = True)
    return df.merge(df_coi, on='VTD')

def community_comparison(partition: Partition, old_state) -> bool:
    proposed_next_state = merge_dfs(partition)
    state = merge_dfs(old_state)
    state_scores = metrics.calculate_all_metrics(state, plan_col='CD_new', lclty_col='cluster', pop_col='TOTPOP')
    proposed_scores = metrics.calculate_all_metrics(proposed_next_state, plan_col='CD_new', lclty_col='cluster', pop_col='TOTPOP')
    return proposed_scores['conditional_entropy']/state_scores['conditional_entropy'], proposed_scores['conditional_entropy'], state_scores['conditional_entropy']

# def community_comparison(partition: Partition, old_state) -> bool:
#     df = pd.DataFrame.from_dict(partition.graph.nodes._nodes, orient='index')
#     # df = df[['VTD', 'TOTPOP']]
#     assign = pd.DataFrame.from_dict(partition.assignment.mapping, orient='index')
#     assign.rename(columns={0:'assignment0'})
#
#     final_df = df.merge(assign, left_index=True, right_index=True)
#     coi_final = final_df.merge(df_coi, on='VTD')
#     print('final df', final_df.head())
#     df_old = pd.DataFrame.from_dict(old_state.graph.nodes._nodes, orient='index')
#     assign_old = pd.DataFrame.from_dict(old_state.assignment.mapping, orient='index')
#     assign_old['assignment0'] = assign_old[0]
#     final_df_old = df.merge(assign_old, left_index=True, right_index=True)
#     coi_final_old = final_df_old.merge(df_coi, on='VTD')
#
#     state = coi_final_old
#     proposed_next_state = coi_final
#
#     state_scores = metrics.calculate_all_metrics(state, 'assignment0', lclty_col='cluster')
#     proposed_scores = metrics.calculate_all_metrics(proposed_next_state, 'assignment0', lclty_col='cluster')
#     return proposed_scores['conditional_entropy'] / state_scores['conditional_entropy'] > 1
#     # return True; #lauren_function(coi_final, coi_final_old) > 1;

def cut_edge_accept(partition: Partition, dummy) -> bool:
    """Always accepts the flip if the number of cut_edges increases.
    Otherwise, uses the Metropolis criterion to decide.

    :param partition: The current partition to accept a flip from.
    :return: True if accepted, False to remain in place

    """
    bound = 1.0

    if partition.parent is not None:
        bound = min(1, len(partition.parent["cut_edges"]) / len(partition["cut_edges"]))

    return random.random() < bound
