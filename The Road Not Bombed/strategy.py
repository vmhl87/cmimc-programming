import random
from copy import deepcopy
from math import sqrt

# How many paths going from (x1, y1) to (x2, y2) contain the point
# (x3, y3)? It surely can't be the same for all of them right?

# If we can answer in general how many paths there are from a to b, then we can answer this probably. Actually not quite right because like you can't backtrack onto yourself hmmmmm but even then it's probably fine for heuristics idk man

# This feels like interesting probability idk

# If we can remove a tile and still have things work, does it necessarily follow that we have better luck removing tiles close to/farther away from that one?

# Lmao what is the probability that a random sample of 100 points actually works well okay we don't really want to choose 100 random points because that doesn't give us connectivity in the case that they're like diagonal or even completely disjoint so what if we pick like orthogonal adjacent neighbors randomly does that even help us. I mean we still need to make sure that we like include a path to get to everyone but like I mean it's worth a shot probably hoepfully we also want to probably get squares in the middle since those are far more accessible so like maybe we get the minimum spanning tree and then add stuff on from there

# Another strategy could just be randomly sampling blocks of like size k by k and then deleting them but I'm not sure that would be very productive ngl

# TODO: Make another planner that literally just dual wields strategies lmao because like we can generate things with the blur initially perchance (like binary search to find the best threshold using only a couple queries) and then use the sampling strategy to take things away perhaps that works better
# Okay this is kinda done

# Okay wait wait what if we did some extra after processing so that if we have floating islands of things (like just stranded ones) we can just remove them because obviously they're not doing anything
# DFS lmao

# We could probably also keep track of each of the grid elements that we're throwing away and if they're not successful multiple times we probably shouldn't choose them as often?

# We should also decrease the number of random samples that we try to pull from the map as the number of queries left approaches 0. Perhaps something like floor(log3(q + 1)) + 1?
# ^ Meh I did something different that probably makes more sense where if the sampling fails a set number of time you just decrease the number of samples

# Hmmm it's not necessarily true that the shortest path between two pairs in a query map is the one that actually allows us to travel between the points so we can't just remove all longer paths (although intuition tells us that the path should be isolated enough if we randomly remove it)

# That being said, we can further refine the notion of isolated points since if we have for example
"""
0#
 #
 #
 ######0
 #
 #
"""
# The bottom two are still in a connected component right but like we absolutely don't need them. So I suppose what we should do is remove all points that are not used in *any* path from one pair to another (just make sure that you remove them after we know that all pairs don't need them). I mean perhaps an interesting path to explore would be checking DFS paths individually but this only really works if the query is already sufficiently sparse enough and also it might take a lot of queries.

# An advantage of this strategy is that, if just even one of the points in some path is removed and the query is successful, we know we can remove literally everything in that path

def pretty_print(query):
    for y in range(16):
        for x in range(16):
            print(int(query[y][x]), end="")
        print()

class Planner:
    def setup(self, pairs, bd):
        self.pairs = pairs
        self.bd = bd

        self.blur_strategy = BlurPlanner()
        self.blur_strategy.setup(pairs, bd)

        self.sample_strategy = SamplingPlanner()
        self.sample_strategy.setup(pairs, bd)

        self.queried = []

    def query(self, q, queryOutputs):
        START = 95
        if q > START:
            result = self.blur_strategy.query(q, queryOutputs)
            self.queried.append(result)

            return result
        elif q == START:
            # Transfer over previous queries to the sample strategy
            for qu in self.queried:
                self.sample_strategy.queried.append(qu)

        return self.sample_strategy.query(q, queryOutputs)

class BlurPlanner:
    def setup(self, pairs, bd):
        self.n = 16

        # Bro why do they store these in (y, x) order
        self.pairs = []
        for pair in pairs:
            self.pairs.append([
                [pair[0][1], pair[0][0]],
                [pair[1][1], pair[1][0]]
            ])

        self.critical_points = []
        
        for [i, j] in self.pairs:
            self.critical_points.append((i[0], i[1]))
            self.critical_points.append((j[0], j[1]))

        buffer = []
        for point in self.critical_points:
            center = self.n // 2
            x = (point[0] + center) // 2
            y = (point[1] + center) // 2 
            buffer.append((x, y))

        # Perhaps interpolate between points more so we can make the decay more
        # strict?
        for point in buffer:
            self.critical_points.append(point)
            
        self.critical_points.append((self.n // 2, self.n // 2))
        
        self.bd = bd

        # queried is a list of tuples of weights and thresholds potentially
        self.queried = []

    def decay(self, dist):
        return 1 / (dist ** 2 + 1)

    def theta(self, weights, x, y):
        p = 0
        
        for k, point in enumerate(self.critical_points):
            dist = sqrt((x - point[0]) ** 2 + (y - point[1]) ** 2)
            p += weights[k] * self.decay(dist)

        return p

    def render(self, weights, threshold):
        return [
            [int(self.theta(weights, x, y) > threshold) for x in range(self.n)]
            for y in range(self.n)
        ]

    def pretty_print(self, weights, threshold):
        grid = self.render(weights, threshold)

        for row in grid:
            for val in row:
                print([" ", "#"][val], end="")
            print()

    def query(self, q, queryOutputs):
        prev = None

        best_threshold = 0
        cap_threshold = 1

        for i, ok in enumerate(queryOutputs):
            if ok:
                prev = self.queried[i]
                best_threshold = max(best_threshold, self.queried[i][1])
            else:
                cap_threshold = min(cap_threshold, self.queried[i][1])

        if not prev:
            # Probably put something different for now but like in the case that
            # we initially do not achieve a filling that works we want to make
            # the threshold less strict
            prev = ([1] * len(self.critical_points), 0.5)
        else:
            # Tweak the weights here I suppose we can binary search the threshold to optimize that I suppose and also we can potentially do some stuff with the coefficients? But that's kinda sus ngl
            prev = (prev[0], (best_threshold + cap_threshold) / 2)
            # print(best_threshold, cap_threshold)
        
        self.queried.append(prev)

        return self.render(prev[0], prev[1])

class SamplingPlanner:
    def setup(self, pairs, bd):
        self.n = 16
        self.pairs = []
        for pair in pairs:
            self.pairs.append([
                [pair[0][1], pair[0][0]],
                [pair[1][1], pair[1][0]]
            ])

        self.pair_points = set()
        for [i, j] in pairs:
            self.pair_points.add((i[0], i[1]))
            self.pair_points.add((j[0], j[1]))
        
        self.bd = bd

        self.queried = []

    def validate(self, query):
        # Returns a pair of a boolean of whether or not its valid
        # Also potentially mutates in place the query to remove any isolated components that are not reached by DFS
        total_visited = [[False for i in range(self.n)] for j in range(self.n)]

        point_list = list(self.pair_points)

        # We must keep track of two different visited matrices
        # - Total visited keeps track of all spots reached across all runs of DFS so we can prune spots that are isolated from any path
        # - Local visited keeps track of all spots reached across a single DFS run so that we know there is a path between the pairs
        # Hopefully this doesn't hurt performance too much (initially I had thought only one DFS was needed but maybe I'm becoming like Joseph fr fr)
        for a, b in self.pairs:
            local_visited = [[False for i in range(self.n)] for j in range(self.n)]
            self.dfs(a[0], a[1], query, total_visited, local_visited)

            if not local_visited[b[1]][b[0]]:
                return False

        for y in range(self.n):
            for x in range(self.n):
                if query[y][x] and not total_visited[y][x]:
                    query[y][x] = 0

        return True

    def dfs(self, x, y, query, total_visited, local_visited):
        if x >= self.n or x < 0 or y >= self.n or y < 0 or local_visited[y][x] or not query[y][x]:
            return

        local_visited[y][x] = True
        total_visited[y][x] = True
        self.dfs(x+1, y, query, total_visited, local_visited)
        self.dfs(x-1, y, query, total_visited, local_visited)
        self.dfs(x, y+1, query, total_visited, local_visited)
        self.dfs(x, y-1, query, total_visited, local_visited)

    def query(self, q, queryOutputs):
        question = []
        prev = None

        # Get last successful query
        for i, ok in enumerate(queryOutputs):
            if ok:
                prev = self.queried[i]

        if prev:
            # Just being safe idk performance shouldn't be an issue
            question = deepcopy(prev)
        else:
            question = [[1 for i in range(self.n)] for j in range(self.n)]

        # 5 seems to work the best ngl
        # as sample size increases, it gets worse
        sample_size = 5 # int(1 / self.bd)
        failed = 0
            
        open = [(i, j) for i in range(16) for j in range(16) if (i, j) not in self.pair_points and question[i][j] == 1]

        # print("Preprint:")
        # pretty_print(question)
        # print("Precheck:", self.validate(question))

        query = deepcopy(question)

        while True:
            # Trust
            query = deepcopy(question)
            random.shuffle(open)
            
            sample = open[:sample_size]
    
            for i in sample:
                query[i[0]][i[1]] = 0

            if self.validate(query):
                break
            else:
                failed += 1

            if failed >= 10:
                failed = 0
                sample_size = max(sample_size - 1, 0)
                # Eventually this will stop query and such if we fail too many times but I don't expect that to happen really it probably won't fail that many times on sample_size = 1 probably hopefully. Just noting that this could possibly a place for more improvement in the future
        
        self.queried.append(query)

        return query

"""
class Planner:
    def setup(self, pairs, bd):
        self.n = 16
        self.pairs = pairs
        self.bd = bd
        self.yeetProbability = 0.07  # probability of removing a road
        self.bestPlan = [[1] * self.n for i in range(self.n)]
        self.sentPlan = []
        return

    def task1(self, q, queryOutputs):  # p = 5, bd = 0.25
        l = len(queryOutputs)
        if l > 0 and queryOutputs[l - 1]:
            self.bestPlan = self.sentPlan
        n = self.n
        newPlan = [[1] * n for i in range(n)]

        # take the most recent successful plan
        # remove each road with small probability
        for i in range(n):
            for j in range(n):
                newPlan[i][j] = self.bestPlan[i][j]
                if newPlan[i][j] == 1:
                    rando = random.uniform(0, 1)
                    if rando < self.yeetProbability:
                        newPlan[i][j] = 0

        self.sentPlan = newPlan
        return self.sentPlan

    def task2(self, q, queryOutputs):
        return self.task1(q, queryOutputs)

    def task3(self, q, queryOutputs):
        return self.task1(q, queryOutputs)

    def task4(self, q, queryOutputs):
        return self.task1(q, queryOutputs)

    def query(self, q, queryOutputs):
        # feel free to modify this function, this is just a suggestion
        if len(self.pairs) == 5 and self.bd == 0.25:
            return self.task1(q, queryOutputs)
        
        if len(self.pairs) == 5 and self.bd == 0.1:
            return self.task2(q, queryOutputs)
        
        if len(self.pairs) == 1 and self.bd == 0.25:
            return self.task3(q, queryOutputs)
        
        if len(self.pairs) == 1 and self.bd == 0.1:
            return self.task4(q, queryOutputs)
        
"""
