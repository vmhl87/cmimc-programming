adj = {}

N = 6

to_int = lambda x, y: N * y + x

for i in range(N):
    for j in range(N):
        adj[to_int(i, j)] = []
        if (i > 0):
            adj[to_int(i, j)].append(to_int(i - 1, j))
        if (i < N - 1):
            adj[to_int(i, j)].append(to_int(i + 1, j))
        if (j > 0):
            adj[to_int(i, j)].append(to_int(i, j - 1))
        if (j < N - 1):
            adj[to_int(i, j)].append(to_int(i, j + 1))

counts = [0 for i in range(N * N)]

# This is mainly just to test time complexity because I'm curious as to whether
# or not the solution is running slow because of some random error or genuinely
# it's just slow

# Roughly like 8.9 s
def dfs_slow(start, target, path):
    path.add(start)

    if start == target:
        for v in list(path):
            counts[v] += 1

        path.remove(start)

        return

    for v in adj[start]:
        if v not in path:
            dfs_slow(v, target, path)

    path.remove(start)

# Like 7.5 s
# One should note that these aren't quite the same but I think for the use case in the path pruning it should be the exact same

# Except nevermind that's just not true because then we'd be keeping track of
# paths that don't even work so perhaps we must just contend with this
def dfs_faster(start, target, path):
    path.add(start)
    counts[start] += 1

    if start == target:
        path.remove(start)
        return

    for v in adj[start]:
        if v not in path:
            dfs_faster(v, target, path)

    path.remove(start)

# Very marginal improvement overall which is sad but like idk

dfs_faster(0, N ** 2 - 1, set())

for i in range(N):
    for j in range(N):
        print(counts[to_int(i, j)], end=" ")
    print()

print(sum(counts))
