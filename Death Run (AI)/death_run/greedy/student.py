import networkx as nx
from math import ceil, inf
import random


class BasedStudent:
    def __init__(
        self, edge_list
    ):
        """
        :param edge_list: A list of tuples representing the edge list of the graph. Tuples are of the
        form (u, v, w), where (u, v) specifies that an edge between vertices u and v exist, and w is the
        weight of that edge.
        :param begin: The label of the vertex which students begin on.
        :param ends: A list of labels of vertices that students may end on (i.e. count as a valid exit).
        """
        pass

    def strategy(
        self,
        edge_updates,
        vertex_count,
        current_vertex
    ):
        """
        :param edge_updates: A dictionary where the key is an edge (u, v) and the value is how much that edge's weight increased in the current round.
        Note that this only contains information about edge updates in the current round, and not previous rounds.
        :param vertex_count: A dictionary where the key is a vertex and the value is how many students are currently on that vertex.
        :param current_vertex: The vertex that you are currently on.
        :return: The label of the vertex to move to. The edge (current_vertex, next_vertex) must exist.
        """
        pass

def dijkstras(graph, source):
    dist = {}
    prev = {}

    queue = set()

    for i in graph:
        dist[i] = inf
        prev[i] = None
        queue.add(i)

    dist[source] = 0

    while queue:
        best = None
        best_dist = inf
        for u in queue:
            if dist[u] <= best_dist:
                best = u
                best_dist = dist[u]

        queue.remove(best)

        for v in graph[best]:
            if v not in queue:
                continue
            alt = dist[best] + graph[best][v]
            if alt < dist[v]:
                dist[v] = alt
                prev[v] = best

    return prev

class RandomStudent(BasedStudent):
    def __init__(self, edge_list, begin, ends):
        self.edge_list = edge_list
        self.begin = begin
        self.ends = ends

    def strategy(self, edge_updates, vertex_count, current_vertex):
        # Take a random out-edge
        return random.choice(
            [
                x
                for (_, x, _) in filter(
                    lambda z: z[0] == current_vertex, self.edge_list
                )
            ]
        )

class BaseStudent(BasedStudent):
    def __init__(self, edge_list, begin, ends):
        self.edge_list = edge_list
        self.begin = begin
        self.ends = ends

        self.in_degrees = {}
        self.out_degrees = {}
        
        self.adj_list = {}

        self.total_criminal_budget = 200

        for i in range(0, 8 * 15 + 1):
            self.in_degrees[i] = 0
            self.out_degrees[i] = 0

            self.adj_list[i] = {}

        for (u, v, w) in self.edge_list:
            self.in_degrees[v] = self.in_degrees[v] + 1
            self.out_degrees[u] = self.out_degrees[u] + 1

            self.adj_list[u] = self.adj_list.get(u, {})
            self.adj_list[u][v] = w

    def strategy(self, edge_updates, vertex_count, current_vertex):
        # Update weights
        for (u, v) in edge_updates:
            self.adj_list[u][v] += edge_updates[(u, v)]

            # Wait just to make sure each student is a separate instance of the
            # class right so we shouldn't have to worry about double counting
            # stuff like this surely surely right
            self.total_criminal_budget -= edge_updates[(u, v)]

        # Form a new graph corresponding to the optimal edge weight penalties
        # assigned by the criminals -> we can probably predict the criminals
        # behavior a little bit better tbh if we actually use our own criminal
        # strategy function inside of here, but for now what we're going to do is
        # just assume that they choose like the optimal weights to target this
        # specific player potentially.

        graph = {}

        # These are the only vertices we need to consider in our case
        current_layer = ceil(current_vertex / 8)
        vertices = [current_vertex]

        for i in range(current_layer * 8 + 1, 15 * 8 + 1):
            vertices.append(i)

        for u in vertices:
            graph[u] = {}

            edges = sorted([(v, self.adj_list[u][v]) for v in self.adj_list[u]], key=lambda a: a[1])

            if len(edges) == 0:
                continue
            elif len(edges) == 1:
                edges[0] = (edges[0][0], edges[0][1] + self.total_criminal_budget)
            elif len(edges) == 2:
                edges[0] = (edges[0][0], edges[0][1] + self.total_criminal_budget / 2)
                edges[1] = (edges[0][0], edges[1][1] + self.total_criminal_budget / 2)
            else:
                edges[0] = (edges[0][0], min(edges[2][1] - edges[0][1], self.total_criminal_budget / 2))
                edges[1] = (edges[0][0], min(edges[2][1] - edges[1][1], self.total_criminal_budget / 2))

            for (v, w) in edges:
                graph[u][v] = w
        
        # Add a last ghost vertex so Dijkstra's actually works
        for i in range(14 * 8 + 1, 15 * 8 + 1):
            graph[i][15 * 8 + 1] = 0.5

        graph[15 * 8 + 1] = {}

        path = dijkstras(graph, current_vertex)

        i = 15 * 8 + 1

        while path[i] != current_vertex:
            i = path[i]
       

        return i
