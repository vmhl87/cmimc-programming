import networkx as nx
import random


# Based fr fr
class BasedCriminal:
    def __init__(
        self, edge_list: list[tuple[int, int, int]], begin: int, ends: list[int]
    ) -> None:
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
        edge_updates: dict[tuple[int, int], int],
        vertex_count: dict[int, int],
        budget: int,
    ) -> tuple[int, int, int]:
        """
        :param edge_updates: A dictionary where the key is an edge (u, v) and the value is how much that edge's weight increased in the previous round.
        Note that this only contains information about edge updates in the previous round, and not rounds before that.
        :param vertex_count: A dictionary where the key is a vertex and the value is how many students are currently on that vertex.
        :param budget: The remaining budget
        :return: Which edge to attack and by how much. Must be a tuple of the form (u, v, w) where (u, v) represents the edge endpoints
        and w is the increase in edge weight. w must be in the range [0, budget].
        """
        pass


class RandomCriminal(BasedCriminal):
    def __init__(self, edge_list, begin, ends):
        self.edge_list = edge_list
        self.begin = begin
        self.ends = ends

    def strategy(self, edge_updates, vertex_count, budget):
        # Find a random populated vertex
        populated_vertices = list(
            filter(lambda z: vertex_count[z], vertex_count.keys())
        )
        vertex = random.choice(populated_vertices)
        # Fill in random out-edge with random weight
        return (
            vertex,
            random.choice(
                [x for (_, x, _) in filter(lambda z: z[0] == vertex, self.edge_list)]
            ),
            random.randint(0, budget),
        )

class BaseCriminal(BasedCriminal):
    def __init__(self, edge_list, begin, ends):
        self.edge_list = edge_list
        self.begin = begin
        self.ends = ends
        
        self.in_degrees = {}
        self.out_degrees = {}
        
        self.adj_list = {}

        for i in range(0, 8 * 15 + 1):
            self.in_degrees[i] = 0
            self.out_degrees[i] = 0

            self.adj_list[i] = {}

        for (u, v, w) in self.edge_list:
            self.in_degrees[v] = self.in_degrees[v] + 1
            self.out_degrees[u] = self.out_degrees[u] + 1

            self.adj_list[u] = self.adj_list.get(u, {})
            self.adj_list[u][v] = w

        for i in range(0, 8 * 15 + 1):
            assert(len(self.adj_list[i]) == self.out_degrees[i])

    def strategy(self, edge_updates, vertex_count, budget):
        # Update weights
        for (u, v) in edge_updates:
            self.adj_list[u][v] += edge_updates[(u, v)]

        assignment = (0, 0, 0)
        best_score = 0

        for i in vertex_count:
            population = vertex_count[i]
            # This can probably be improved upon a lot later but we'll see

            # If the outdegree is greater than or equal to 2, we we shall assign
            # a penalty corresponding to the difference between the two smallest
            # edge weights -> this guarantees population * min edge weight

            # If there's only one edge then the answer is trivial trust trust

            # This greedy assignment of weights likely fails to take into that
            # the students could move to a better spot for us the future (say an
            # outdegree of 1 vertex) and it also doesn't communicate well with the
            # other criminal.

            if self.out_degrees[i] == 0:
                continue

            if self.out_degrees[i] == 1:
                expected_score = population * budget
                s = (i, list(self.adj_list.keys())[0], budget)
            else:
                nexts = sorted(self.adj_list[i].keys(), key=lambda v: self.adj_list[i][v])
                weights = sorted(self.adj_list[i].values())
                expected_score = population * min(budget, weights[1] - weights[0])
                s = (i, nexts[0], min(budget, weights[1] - weights[0]))

            if expected_score > best_score:
                best_score = expected_score
                assignment = s

        return assignment
                
