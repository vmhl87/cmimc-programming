import random

GRID_RADIUS = 3
node_coordinates = []
ALL_NEIGHBOR = lambda x, y, z: ((x + 1, y, z), (x - 1, y, z), (x, y + 1, z), (x, y - 1, z), (x, y, z + 1), (x, y, z - 1)) # make this more efficient?
SELECT_VALID = lambda lis: [(x, y, z) for (x, y, z) in lis if 1 <= x + y + z <= 2 and -GRID_RADIUS + 1 <= x <= GRID_RADIUS and -GRID_RADIUS + 1 <= y <= GRID_RADIUS and -GRID_RADIUS + 1 <= z <= GRID_RADIUS] # keep those within-bound
TABLE = {1:0, 2:0, 3:1, 4:3, 5:0}

for x in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
    for y in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
        for z in range(-GRID_RADIUS + 1, GRID_RADIUS + 1):
            # Check if node is valid
            if 1 <= x + y + z <= 2:
                node_coordinates.append((x, y, z))
NEIGHBOR_LIST = dict(zip(node_coordinates, [SELECT_VALID(ALL_NEIGHBOR(*(node))) for node in node_coordinates]))

def get_diameter(board, start_node, visit): 
    def neighbors(node):
        #return SELECT_VALID(ALL_NEIGHBOR(*(node)))
        return NEIGHBOR_LIST[node]
    def con(node): # Find connected component and respective degrees
        visit[node] = 1
        connected[node] = -1
        cnt = 0
        for neighbor in neighbors(node):
            if neighbor in board and board[neighbor] == player:
                cnt += 1
                if neighbor not in connected:
                    con(neighbor)
        connected[node] = cnt
    def dfs(node, visited = set()):
        visited.add(node)
        max_path_length = 0
        for neighbor in neighbors(node):
            if neighbor in board and board[neighbor] == player and neighbor not in visited:
                path_length = dfs(neighbor, visited.copy())
                max_path_length = max(max_path_length, path_length)
        return max_path_length + 1

    try:
        player = board[start_node]
    except Exception as exc:
        print("node empty?")
        print(exc)
        return 0

    connected = dict()
    con(start_node)
    #print(connected)
    if len(connected) <= 3: # must be a line
        return len(connected)
    if 4 <= len(connected) <= 5: # a star if we have a deg-3 node, a line otherwise
        if 3 in connected.values(): # It's a star!
            return len(connected) - 1
        return len(connected)
    if 6 == len(connected):
        three = list(connected.values())
        if 3 in connected.values():
            three.remove(3)
            if 3 in connected.values():
                return 4 # this is a shape x - x - x - x
                        #                     x   x
        return 5 # diameter is 5 otherwise

    # For the larger(>6) ones, diameter must be larger than 5 so we just return 5
    return 5
    # maxl = 0

    # for node in connected:
    #     maxl = max(maxl, dfs(node))
    # return maxl
def score(board): # return current score for each player
    visit = {pos:0 for pos in node_coordinates}
    scores = {0:0 , 1:0, 2:0}
    for pos in board.keys():
        if not visit[pos]:
            d = get_diameter(board, pos, visit)
            if d:
                scores[board[pos]] += TABLE[d]
    return scores
    
def defense_points(board, player):
    pts = []
    for pt in node_coordinates:
        pass
    return pts
    
def bot_move(board, player):
    current_score = score(board)
    top_score = max(max(current_score[0], current_score[1]), current_score[2])
    my_score = current_score[player]

    node_depth = {}
    vis = []
    cur = []
    for pt in node_coordinates:
        if(len(NEIGHBOR_LIST[pt]) == 2):
            node_depth[pt] = 0
            vis.append(pt)
            cur.append(pt)

    dep = 1
    while(True):
        nxt = []
        for pt in cur:
            for pt2 in NEIGHBOR_LIST[pt]:
                if(pt2 not in vis and pt2 not in nxt):
                    nxt.append(pt2)
        for pt in nxt:
            node_depth[pt] = dep
        dep += 1
        cur = [pt for pt in nxt]

        if(len(cur) == 0):
            break

    print(node_depth)

    # Find handicaps
    empty_nodes = [node for node in node_coordinates if node not in board and get_diameter(board.copy(), node, player) < 5]

    if len(empty_nodes)==0:
        return None
    # Choose a random move
    return random.choice(empty_nodes)
    
    # go for the edges of the board, work your way in over the course of the game
    # aim to create groups of 3 through a center and any 2 of 3 points surrounding the center
    #     - create a 4 by continuing the 3
    # if possible to create a group of 3/4, must create that group in an optimal fashion
    #     - create a group while also blocking another person's group
    # NEVER CREATE A 5
    
    # if an opponent only has one way to make a 3/4, block them if them getting the point means they will overtake your score
    #     - and if you have more than one way to get a 3/4
