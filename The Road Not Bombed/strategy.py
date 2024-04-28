import random
from copy import deepcopy
from math import sqrt, floor, log
import sys

# How many paths going from (x1, y1) to (x2, y2) contain the point
# (x3, y3)? It surely can't be the same for all of them right?

# If we can answer in general how many paths there are from a to b, then we can
# answer this probably. Actually not quite right because like you can't
# backtrack onto yourself hmmmmm but even then it's probably fine for
# heuristics idk man

# This feels like interesting probability idk

# If we can remove a tile and still have things work, does it necessarily
# follow that we have better luck removing tiles close to/farther away from
# that one?

# Lmao what is the probability that a random sample of 100 points actually
# works well okay we don't really want to choose 100 random points because that
# doesn't give us connectivity in the case that they're like diagonal or even
# completely disjoint so what if we pick like orthogonal adjacent neighbors
# randomly does that even help us. I mean we still need to make sure that we
# like include a path to get to everyone but like I mean it's worth a shot
# probably hoepfully we also want to probably get squares in the middle since
# those are far more accessible so like maybe we get the minimum spanning tree
# and then add stuff on from there

# Another strategy could just be randomly sampling blocks of like size k by k
# and then deleting them but I'm not sure that would be very productive ngl

# TODO: Make another planner that literally just dual wields strategies lmao
# because like we can generate things with the blur initially perchance (like
# binary search to find the best threshold using only a couple queries) and
# then use the sampling strategy to take things away perhaps that works better
# Okay this is kinda done

# Okay wait wait what if we did some extra after processing so that if we have
# floating islands of things (like just stranded ones) we can just remove them
# because obviously they're not doing anything
# DFS lmao

# We could probably also keep track of each of the grid elements that we're
# throwing away and if they're not successful multiple times we probably
# shouldn't choose them as often?

# We should also decrease the number of random samples that we try to pull from
# the map as the number of queries left approaches 0. Perhaps something like
# floor(log3(q + 1)) + 1?
# ^ Meh I did something different that probably makes more sense where if the
# sampling fails a set number of time you just decrease the number of samples

# Hmmm it's not necessarily true that the shortest path between two pairs in a
# query map is the one that actually allows us to travel between the points so
# we can't just remove all longer paths (although intuition tells us that the
# path should be isolated enough if we randomly remove it)

# That being said, we can further refine the notion of isolated points since if
# we have for example
"""
0#
 #
 #
 ######0
 #
 #
"""
# The bottom two are still in a connected component right but like we
# absolutely don't need them. So I suppose what we should do is remove all
# points that are not used in *any* path from one pair to another (just make
# sure that you remove them after we know that all pairs don't need them). I
# mean perhaps an interesting path to explore would be checking DFS paths
# individually but this only really works if the query is already sufficiently
# sparse enough and also it might take a lot of queries.

# An advantage of this strategy is that, if just even one of the points in some
# path is removed and the query is successful, we know we can remove literally
# everything in that path

# Wait perhaps a more performant way to do this is possible because perhaps
# the really slow DFS where we consider all paths isn't the most performant way
# of doing things.

# We may observe the paths in the query based on the number of neighbors they
# have that are colored in and form a new graph based on it. More specifically,
# let all points with 3 or 4 neighbors be vertices on a graph as well as the
# specific pair points, and the paths between them with vertices that contain 1
# or 2 neighbors can be represented as the edges. This way, the paths that
# don't lead anywhere aren't even considered as edges in this graph and then we
# can just do DFS like normal on the connected components?

# Okay well I think one has to make this idea a bit more precise and
# potentially the number of neighbors isn't the best way to decide the control
# points but I'm curious as to whether this preprocessing will actually speed
# up the slower DFS any more to be useful enough. I mean it's essentially the
# same sort of algorithm except we're compressing the graph in a way I suppose
# so hopefully that will help with the compute time.


# TODO: Implement counting of the spots that we have queried to weight the
# probability of choosing them again in the future. Probably I'll have to make
# my own weighted sampler because random.choices uses sampling with replacement
# because idk it's probably easier to implement <- DONE

# Wow I really need to stop yapping fr.

# Weighting type 1
def count_to_weight(count):
    if count >= 5:
        return 0.05

    return [1, 0.8, 0.4, 0.2, 0.1][count]

def weighted_sampler(points, weights, n):
    assert len(points) == len(weights)

    n = min(len(points), n)

    sample = set()
    total = sum(weights)

    while len(sample) < n:
        r = random.uniform(0, 1) * total

        for i, w in enumerate(weights):
            if points[i] in sample:
                continue

            if r < w:
                sample.add(points[i])
                # Remember to subtract the weights properly dawg
                total -= w
                break
            else:
                r -= w

    return list(sample)

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
        prev = None

        if q > START:
            result = self.blur_strategy.query(q, queryOutputs)
            self.queried.append(result)

            return result
        elif q == START:
            # Transfer over previous queries to the sample strategy
            for qu in self.queried:
                self.sample_strategy.queried.append(qu)

            for i, (query, threshold) in enumerate(self.blur_strategy.queried):
                if prev is None or threshold > prev[1]:
                    prev = (self.queried[i], threshold)

        return self.sample_strategy.query(q, queryOutputs, None if prev is None else prev[0])

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

        # self.fill_critical_points_centering()
        self.fill_critical_points_interpolating()
        
        self.bd = bd

        # queried is a list of tuples of weights and thresholds potentially
        self.queried = []

    def fill_critical_points_centering(self):
        for [i, j] in self.pairs:
            self.critical_points.append((i[0], i[1]))
            self.critical_points.append((j[0], j[1]))

        buffer = []
        for point in self.critical_points:
            center = self.n / 2
            midx = (point[0] + center) / 2
            midy = (point[1] + center) / 2 

            buffer.append((midx, midy))

        # Perhaps interpolate between points more so we can make the decay more
        # strict?
        for point in buffer:
            self.critical_points.append(point)
            
        self.critical_points.append((self.n / 2, self.n / 2))
        
    def fill_critical_points_interpolating(self):
        for [i, j] in self.pairs:
            leftx, lefty = i[0], i[1]
            rightx, righty = j[0], j[1]

            midx, midy = (leftx + rightx) / 2, (lefty + righty) / 2
            leftmidx, leftmidy = (leftx + midx) / 2, (lefty + midy) / 2
            rightmidx, rightmidy = (rightx + midx) / 2, (righty + midy) / 2

            self.critical_points.append((leftx, lefty))
            self.critical_points.append((midx, midy))
            self.critical_points.append((leftmidx, leftmidy))
            self.critical_points.append((rightmidx, rightmidy))
            self.critical_points.append((rightx, righty))

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
        cap_threshold = 1.5

        for i, ok in enumerate(queryOutputs):
            if ok:
                prev = self.queried[i]
                best_threshold = max(best_threshold, self.queried[i][1])
            else:
                cap_threshold = min(cap_threshold, self.queried[i][1])

        if q == 100:
            # Probably put something different for now but like in the case that
            # we initially do not achieve a filling that works we want to make
            # the threshold less strict
            prev = ([1] * len(self.critical_points), 0.3)
        else:
            # Tweak the weights here I suppose we can binary search the
            # threshold to optimize that I suppose and also we can potentially
            # do some stuff with the coefficients? But that's kinda sus ngl

            # Actually I'll hold off on tweaking the weights since that seems suboptimal
            prev = ([1] * len(self.critical_points), (best_threshold + cap_threshold) / 2)
            # print(best_threshold, cap_threshold)
        
        self.queried.append(prev)

        result = self.render(prev[0], prev[1])

        # print("Threshold:", prev[1])
        # pretty_print(result)

        return result

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

        self.counts = [[0 for i in range(self.n)] for j in range(self.n)]
        self.prev_sampled = []

        self.queried = []

    def validate(self, query, force=False):
        # Returns a pair of a boolean of whether or not its valid
        # Also potentially mutates in place the query to remove any isolated components that are not reached by DFS
        total_visited = [[False for i in range(self.n)] for j in range(self.n)]

        point_list = list(self.pair_points)

        count = sum(query[i][j] for i in range(self.n) for j in range(self.n))
        # Okay dfsTarget is really inefficient so like unfortunately we just
        # can't use it really
        sparse = (count < 70 or force) and False

        # Due to how slow dfsTarget() is (which is really just a consequence of
        # what it's trying to do idk if you can really make it any faster) we
        # probably only really want to use it a couple times which is why I
        # have it only run when the graph is sparse enough.
        # Otherwise yeah it essentially just hangs because there are too many
        # paths.

        # Perhaps we could just put it at the end to clean things up but like idk there could be non-trivial benefits to running it during the sampling stage
        for a, b in self.pairs:
            local_visited = [[False for i in range(self.n)] for j in range(self.n)]
            
            if sparse:
                if not self.dfsTarget(a[0], a[1], b[0], b[1], query, total_visited, set()):
                    return False
            else:
                self.dfsSimple(a[0], a[1], query, total_visited, local_visited)

                if not local_visited[b[1]][b[0]]:
                    return False

        for y in range(self.n):
            for x in range(self.n):
                if query[y][x] and not total_visited[y][x]:
                    query[y][x] = 0

        return True

    def dfsSimple(self, x, y, query, total_visited, local_visited):
        if x >= self.n or x < 0 or y >= self.n or y < 0 or local_visited[y][x] or not query[y][x]:
            return

        local_visited[y][x] = True
        total_visited[y][x] = True
        self.dfsSimple(x+1, y, query, total_visited, local_visited)
        self.dfsSimple(x-1, y, query, total_visited, local_visited)
        self.dfsSimple(x, y+1, query, total_visited, local_visited)
        self.dfsSimple(x, y-1, query, total_visited, local_visited)

    def dfsTarget(self, x, y, target_x, target_y, query, total_visited, current_path):
        if x >= self.n or x < 0 or y >= self.n or y < 0 or not query[y][x]:
            return False
        elif (x, y) in current_path:
            return False

        current_path.add((x, y))

        if (x, y) == (target_x, target_y):
            for point in list(current_path):
                total_visited[point[1]][point[0]] = True

            current_path.remove((x, y))

            return True

        right = self.dfsTarget(x+1, y, target_x, target_y, query, total_visited, current_path)
        left  = self.dfsTarget(x-1, y, target_x, target_y, query, total_visited, current_path)
        down  = self.dfsTarget(x, y+1, target_x, target_y, query, total_visited, current_path)
        up    = self.dfsTarget(x, y-1, target_x, target_y, query, total_visited, current_path)

        current_path.remove((x, y))

        return right or left or up or down

    def query(self, q, queryOutputs, prev_query=None):
        # If the previous query failed, we should update the counts
        if not queryOutputs[-1]:
            for (y, x) in self.prev_sampled:
                self.counts[y][x] += 1

        self.prev_sampled = []
        question = []
        prev = prev_query

        # Get last successful query
        for i, ok in enumerate(queryOutputs):
            if ok and prev_query is None:
                prev = self.queried[i]

        if prev:
            # Just being safe idk performance shouldn't be an issue
            question = deepcopy(prev)
        else:
            question = [[1 for i in range(self.n)] for j in range(self.n)]

        # 5 seems to work the best ngl
        # as sample size increases, it gets worse
        # Perhaps we should just like decrease this over time as the number of
        # queries runs out
        sample_size = floor(log(q + 1, 3)) + 1 # 5 # int(1 / self.bd)
        failed = 0
            
        open = [(y, x) for y in range(self.n) for x in range(self.n) if (y, x) not in self.pair_points and question[y][x] == 1]
        weights = [count_to_weight(self.counts[y][x]) for (y, x) in open]

        # print("Preprint:")
        # pretty_print(question)
        # print("Precheck:", self.validate(question))

        query = deepcopy(question)

        while sample_size:
            # Trust
            query = deepcopy(question)
            # random.shuffle(open)
            # sample = open[:sample_size]
            sample = weighted_sampler(open, weights, sample_size)
    
            for i in sample:
                query[i[0]][i[1]] = 0

            if self.validate(query, False):
                self.prev_sampled = sample

                break
            else:
                failed += 1

            if failed >= 20:
                failed = 0
                sample_size = max(sample_size - 1, 0)
                # Eventually this will stop querying and such if we fail too
                # many times but I don't expect that to happen really it
                # probably won't fail that many times on sample_size = 1
                # probably hopefully. Just noting that this could possibly a
                # place for more improvement in the future
        
        self.queried.append(query)

        return query
