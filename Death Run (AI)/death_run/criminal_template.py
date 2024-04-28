import networkx as nx
import random

# Based fr fr
# class BasedCriminal:
#     def __init__(
#         self, edge_list
#     ):
#         """
#         :param edge_list: A list of tuples representing the edge list of the graph. Tuples are of the
#         form (u, v, w), where (u, v) specifies that an edge between vertices u and v exist, and w is the
#         weight of that edge.
#         :param begin: The label of the vertex which students begin on.
#         :param ends: A list of labels of vertices that students may end on (i.e. count as a valid exit).
#         """
#         pass
# 
#     def strategy(
#         self,
#         edge_updates,
#         vertex_count,
#         budget
#     ):
#         """
#         :param edge_updates: A dictionary where the key is an edge (u, v) and the value is how much that edge's weight increased in the previous round.
#         Note that this only contains information about edge updates in the previous round, and not rounds before that.
#         :param vertex_count: A dictionary where the key is a vertex and the value is how many students are currently on that vertex.
#         :param budget: The remaining budget
#         :return: Which edge to attack and by how much. Must be a tuple of the form (u, v, w) where (u, v) represents the edge endpoints
#         and w is the increase in edge weight. w must be in the range [0, budget].
#         """
#         pass


class BaseCriminal:
    def __init__(self, edge_list, begin, ends):
        self.edge_list = edge_list
        self.begin = begin
        self.ends = ends

    def strategy(self, edge_updates, vertex_count, budget):
        return
                
