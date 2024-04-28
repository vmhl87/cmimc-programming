from random import randint

MINIMAX_DEPTH = 4

def pretty_print(graph):
    for i in graph:
        print(i, "{", end=" ")
        
        for index, j in enumerate(sorted(graph[i].keys())):
            print(j, "->", graph[i][j], end=", " if index != len(graph[i]) - 1 else "")
        print(" }")

class State:
    def __init__(self, to, weight):
        self.to = to
        self.weight = weight

    def __lt__(self, other):
        # A state is considered better iff self.weight < other.weight
        # We consider better states to be larger (higher student score)
        # and worse states to be smaller (higher criminal score, although we
        # don't quite measure in terms of the criminal because this is the
        # student strategy and that doesn't matter)
        return self.weight > other.weight

class CriminalStrategy:
    def __init__(self, base):
        self.base = base
        self.budget = 100

    def moves(self, pos):
        outdegree = len(self.base.graph[pos])
        assert outdegree > 0

        # This can definitely be improved later but for now let's just pick
        # criminal moves somewhat greedily just like before
        move_list = []

        # Doing nothing is always an option trust trust
        # Life lesson fr
        # actually no that's terrible life advice
        first_vertex = list(self.base.graph[pos].keys())[0]
        move_list.append((pos, first_vertex, 0))

        if outdegree == 1:
            move_list.append(
                (pos, first_vertex, self.budget)
            )
        else:
            nexts = sorted(self.base.graph[pos].keys(), key=lambda v: self.base.graph[pos][v] + sum(self.base.penalties[pos][v]))
            weights = sorted(
                self.base.graph[pos][i] + sum(self.base.penalties[pos][i])
                for i in self.base.graph[pos]
            )

            move_list.append(
                (pos, nexts[0], min(self.budget, weights[1] - weights[0]))
            )

        return move_list

    def do_move(self, move):
        self.budget -= move[2]
        assert self.budget >= 0

        self.base.penalties[move[0]][move[1]].append(move[2])

    def undo_move(self, move):
        self.budget += move[2]

        self.base.penalties[move[0]][move[1]].pop()

class StudentStrategy:
    def __init__(self, base, start):
        self.base = base
        self.pos = start

    def moves(self):
        return [i for i in self.base.graph[self.pos]]

class BaseStudent:
    def __init__(self, edge_list, begin, ends):
        self.edge_list = edge_list
        self.begin = begin
        self.targets = set(ends)

        self.graph = {}
        self.penalties = {}

        for (u, v, w) in edge_list:
            if u not in self.graph:
                self.graph[u] = {}
                self.penalties[u] = {}

            self.graph[u][v] = w
            self.penalties[u][v] = []

        # pretty_print(self.graph)

        self.our_criminal = CriminalStrategy(self)
        self.their_criminal = CriminalStrategy(self)
        self.student = StudentStrategy(self, begin)

    def minimax(self, is_criminal, is_ours, depth=0):
        if is_criminal:
            best_state = None
            criminal = self.our_criminal if is_ours else self.their_criminal

            for move in criminal.moves(self.student.pos):
                criminal.do_move(move)

                if is_ours:
                    state = self.minimax(True, False, depth)
                else:
                    state = self.minimax(False, True, depth)

                # Evaluations are viewed from the student so we want the
                # smallest score to optimize the criminal move
                if best_state is None or state < best_state:
                    best_state = state

                criminal.undo_move(move)

            return best_state
        else:
            best_state = None

            for move in self.student.moves():
                current = self.student.pos

                weight = self.graph[current][move] + sum(self.penalties[current][move])

                self.student.pos = move

                if depth == MINIMAX_DEPTH or move in self.targets:
                    state = State(move, weight)
                else:
                    state = self.minimax(True, True, depth + 1)
                    state.weight += weight

                if best_state is None or state > best_state:
                    best_state = state
                    best_state.to = move

                self.student.pos = current

            return best_state

    def strategy(self, edge_updates, vertex_count, current_index):
        if current_index in self.targets:
            # I wonder if this is needed
            return None

        self.student.pos = current_index

        # This should update the stuff in the other strategy objects because
        # pass by reference trust trust
        for update in edge_updates:
            self.penalties[update[0]][update[1]].append(edge_updates[update])

        state = self.minimax(False, True)

        return state.to
