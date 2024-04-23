import random

GRID_RADIUS = 4
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
        # print("node empty?")
        # print(exc)
        return 0

    connected = dict()
    con(start_node)
    # print(connected)
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
    opponents = [0, 1, 2]
    opponents.remove(player)
    opponents.sort(key=lambda opp: -score(board)[opp])
    block_points = []
    for i in range(len(opponents)):
        opp = opponents[i]
        for pt in node_coordinates:
            amt = 0
            for pt2 in NEIGHBOR_LIST[pt]:
                if(pt2 in board and board[pt2] == opp):
                    amt += 1

            if(pt in board and board[pt] == opp and amt == 1):
                vis = []
                def dfs(cur, path):
                    ok = False
                    vis.append(cur)
                    for nxt in NEIGHBOR_LIST[cur]:
                        if(nxt not in vis and nxt in board and board[nxt] == opp):
                            ok = True
                            dfs(nxt, path + [nxt])

                    if(not ok):
                        if(len(path) < 4):
                            open_points = []
                            for pt2 in NEIGHBOR_LIST[path[0]]:
                                if(pt2 not in board):
                                    open_points.append(pt2)
                            for pt2 in NEIGHBOR_LIST[path[-1]]:
                                if(pt2 not in board):
                                    open_points.append(pt2)

                            good_points = []
                            for pt2 in open_points:
                                prev_score = score(board)[opp]
                                board[pt2] = opp
                                if(score(board)[opp] >= prev_score):
                                    good_points.append(pt2)
                                del board[pt2]

                            for pt2 in good_points:
                                prev_score = score(board)[player]
                                board[pt2] = player
                                block_point = []
                                if(len(good_points) == 1):
                                    block_point = [pt2, opp, len(path)+1]
                                elif(len(good_points) > 1):
                                    block_point = [pt2, opp, -1000 + len(path)]
                                if(score(board)[player] >= prev_score and block_point not in block_points):
                                    block_points.append(block_point)
                                del board[pt2]

                dfs(pt, [pt])
    block_points.sort(key=lambda pt: 100*opponents.index(pt[1])-pt[2])

    return block_points

def cmp(pt, block_points):
    for pair in block_points:
        if(pair[0] == pt):
            return -pair[2]
    return 10000

def bot_move(board, player):
    # print("move number:",len(board))
    current_score = score(board)
    top_score = max(max(current_score[0], current_score[1]), current_score[2])
    my_score = current_score[player]

    depth = {}
    vis = []
    cur = []
    for pt in node_coordinates:
        if(len(NEIGHBOR_LIST[pt]) == 2):
            depth[pt] = 0
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
            depth[pt] = dep
            vis.append(pt)

        dep += 1
        cur = [pt for pt in nxt]

        if(len(cur) == 0):
            break

    node_depth = {}
    for key in depth:
        if(depth[key] in node_depth):
            node_depth[depth[key]].append(key)
        else:
            node_depth[depth[key]] = [key]

    node_paths = []
    for pt in node_coordinates:
        if(pt in board):
            continue
        vis = []
        def dfs(cur, path, len_path):
            if(len(path) == len_path):
                ok = True
                for pt2 in path:
                    for pt3 in NEIGHBOR_LIST[pt2]:
                        if(pt3 in board and board[pt3] == player):
                            ok = False
                if(ok):
                    node_paths.append(path)
                return
            vis.append(cur)
            for nxt in NEIGHBOR_LIST[cur]:
                if(nxt not in vis and nxt not in board):
                    path.append(nxt)
                    dfs(nxt, path.copy(), len_path)
                    path = path[:len(path)-1]
        dfs(pt, [pt], 4)
        vis = []
        dfs(pt, [pt], 3)

    current_obj = None

    for pt in node_coordinates:
        if(pt in board and board[pt] == player):
            path = []
            def dfs(cur):
                path.append(cur)
                for nxt in NEIGHBOR_LIST[cur]:
                    if(nxt not in path and nxt in board and board[nxt] == player):
                        dfs(nxt)

            dfs(pt)

            if(len(path) == 4):
                continue

            endpoints = []
            for pt2 in path:
                amt = 0
                for pt3 in NEIGHBOR_LIST[pt2]:
                    if(pt3 in board and board[pt3] == player):
                        amt += 1

                if(amt == 1 or amt == 0):
                    endpoints.append(pt2)

            ok = False
            for pt2 in endpoints:
                for pt3 in NEIGHBOR_LIST[pt2]:
                    if(pt3 not in board):
                        ok = True

            if(ok):
                current_obj = [pt2 for pt2 in path]
                for pt2 in endpoints:
                    current_obj.remove(pt2)
                if(len(endpoints) == 2):
                    current_obj = [endpoints[0]] + current_obj + [endpoints[1]]
                elif(len(endpoints) == 1):
                    current_obj = [pt2 for pt2 in endpoints]

    path_containing_node = {}
    for pt in node_coordinates:
        path_containing_node[pt] = 0

    # print("current_obj:",current_obj)
    current_paths = 0
    # print(node_paths)
    for path in node_paths:
        # print(path)
        if(current_obj != None):
            ok = True
            for pt in current_obj:
                if(pt not in path):
                    ok = False
            if(ok):
                current_paths += 1

        for pt in path:
            path_containing_node[pt] += 1

    nodes = [c for c in node_coordinates]
    choice = None
    block_points = defense_points(board, player)
    # print("current_paths:",current_paths)
    # print("block_points:",block_points)
    # if(len(block_points) != 0):
        # print("a;lskdfj;alsdkjfa;slkdjf;ajskd;lasdlf;kajsd;lfkjasd;lkfjals;dkjf;askdflakjsd;fkjas;dkjfas;lkdjl;askjdf;lakjsd;lfkjas;dlfjka;ksdf")
        # print("a;lskdfj;alsdkjfa;slkdjf;ajskd;lasdlf;kajsd;lfkjasd;lkfjals;dkjf;askdflakjsd;fkjas;dkjfas;lkdjl;askjdf;lakjsd;lfkjas;dlfjka;ksdf")
        # print("a;lskdfj;alsdkjfa;slkdjf;ajskd;lasdlf;kajsd;lfkjasd;lkfjals;dkjf;askdflakjsd;fkjas;dkjfas;lkdjl;askjdf;lakjsd;lfkjas;dlfjka;ksdf")
        # print("a;lskdfj;alsdkjfa;slkdjf;ajskd;lasdlf;kajsd;lfkjasd;lkfjals;dkjf;askdflakjsd;fkjas;dkjfas;lkdjl;askjdf;lakjsd;lfkjas;dlfjka;ksdf")
    if(current_obj == None):
        # print("num paths containing node:",path_containing_node)
        nodes.sort(key=lambda pt: -path_containing_node[pt])
        possible = []
        mx_paths = path_containing_node[nodes[0]]

        for pt in nodes:
            if(pt not in board):
                ok = True
                for pt2 in NEIGHBOR_LIST[pt]:
                    if(pt2 in board and board[pt2] == player):
                        ok = False
                if(ok and path_containing_node[pt] == mx_paths):
                    possible.append(pt)

        possible.sort(key=lambda pt: cmp(pt,block_points))
        # print("possible:",mx_possible)
        if(len(possible) > 0 and mx_paths > 0):
            choice = possible[0]
    # elif(len(block_points) > 0 and block_points[0][2] > 0 and current_score[block_points[0][1]] + TABLE[block_points[0][2]] - TABLE[block_points[0][2]-1] > my_score):
    # # if(len(block_points) > 0):
    #     choice = block_points[0][0]
    else:
        moves = []
        for pt in NEIGHBOR_LIST[current_obj[0]]:
            if(pt not in board):
                moves.append([pt, "front"])

        for pt in NEIGHBOR_LIST[current_obj[-1]]:
            if(pt not in board):
                moves.append([pt, "back"])

        # print("moves:", moves)
        # print(node_paths)
        best_point = None
        max_opp = 0
        pt_opp = {}
        for pair in moves:
            pt = pair[0]
            if(pair[1] == "front"):
                current_obj = [pt] + current_obj
            else:
                current_obj.append(pt)

            amt = [0]
            vis = [pt2 for pt2 in current_obj]
            def dfs(cur, dep, len_path):
                for pt2 in NEIGHBOR_LIST[cur]:
                    if(pt2 in board and board[pt2] == player and pt2 not in vis):
                        return

                if(dep == len_path):
                    amt[0] += 1
                    return

                vis.append(cur)
                for nxt in NEIGHBOR_LIST[cur]:
                    if(nxt not in vis and nxt not in board):
                        dfs(nxt, dep + 1, len_path)

            for i in range(-1, 1):
                for j in range(3, 5):
                    vis = [pt2 for pt2 in current_obj]
                    dfs(current_obj[i], len(current_obj),j)

            if(pair[1] == "front"):
                current_obj = current_obj[1:]
            else:
                current_obj = current_obj[:len(current_obj)-1]

            # # print("amt:", amt[0])
            for pt2 in NEIGHBOR_LIST[pt]:
                if(pt2 in board and board[pt2] == player and pt2 not in current_obj):
                    amt[0] = 0

            max_opp = max(max_opp, amt[0])
            if(amt[0] in pt_opp):
                pt_opp[amt[0]].append(pt)
            else:
                pt_opp[amt[0]] = [pt]

        # print(best_point != pt_opp[max_opp][0])
        # pt_opp[max_opp].sort(key=lambda pt: cmp(pt, block_points))
        if(max_opp != 0):
            choice = pt_opp[max_opp][0]

    if(choice == None):
        for pt in block_points:
            ok = True
            for pt2 in NEIGHBOR_LIST[pt[0]]:
                if(pt2 in board and board[pt2] == player):
                    ok = False
            if(ok):
                choice = pt[0]

        # if(choice == None):
        #     for pt in node_coordinates:
        #         if(pt not in board):
        #             prev_score = score(board)[player]
        #             board[pt] = player
        #             if(score(board)[player] >= prev_score):
        #                 del board[pt]
        #                 return pt
        #             del board[pt]
    return choice

    # go for the edges of the board, work your way in over the course of the game
    # aim to create groups of 3 through a center and any 2 of 3 points surrounding the center
    #     - create a 4 by continuing the 3
    # if possible to create a group of 3/4, must create that group in an optimal fashion
    #     - create a group while also blocking another person's group
    # NEVER CREATE A 5

    # if an opponent only has one way to make a 3/4, block them if them getting the point means they will overtake your score
    #     - and if you have more than one way to get a 3/4

