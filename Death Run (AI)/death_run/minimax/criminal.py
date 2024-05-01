from random import randint

MINIMAX_DEPTH = 2

def pretty_print(graph):
    for i in graph:
        print(i, "{", end=" ")
        
        for index, j in enumerate(sorted(graph[i].keys())):
            print(j, "->", graph[i][j], end=", " if index != len(graph[i]) - 1 else "")
        print(" }")

class State:
    def __init__(self, move, score, weight):
        self.move = move
        self.score = score
        self.weight = weight

    def better_for_criminal(self, other):
        # We are viewing the score from the criminal's point of view, so the
        # higher the number the better.
        return self.score > other.score

    def better_for_student(self, other):
        # Looking from the student perspective, a lower total weight is better
        return self.weight < other.weight

class CriminalStrategy:
    def __init__(self, base):
        self.base = base
        self.budget = 100

    def moves(self, pos):
        outdegree = len(self.base.graph[pos])
        # assert outdegree > 0

        # This can definitely be improved later but for now let's just pick
        # criminal moves somewhat greedily just like before
        move_list = []

        first_vertex = list(self.base.graph[pos].keys())[0]
        move_list.append((pos, first_vertex, 0))

        if outdegree == 1:
            move_list.append(
                (pos, first_vertex, self.budget)
            )
        else:
            nexts = sorted(self.base.graph[pos].keys(), key=lambda v: self.base.graph[pos][v] + sum(p[0] for p in self.base.penalties[pos][v]))
            weights = sorted(
                self.base.graph[pos][i] + sum(p[0] for p in self.base.penalties[pos][i])
                for i in self.base.graph[pos]
            )

            # Trust trust
            place = max(0, weights[1] - weights[0])

            move_list.append(
                (pos, nexts[0], min(self.budget, place))
            )

            move_list.append(
                (pos, nexts[0], self.budget // 10)
            )

        return move_list

    def do_move(self, move, is_ours):
        self.budget -= move[2]
        # assert self.budget >= 0

        self.base.penalties[move[0]][move[1]].append((move[2], is_ours))

    def undo_move(self, move):
        self.budget += move[2]

        self.base.penalties[move[0]][move[1]].pop()

class StudentStrategy:
    def __init__(self, base, start):
        self.base = base
        self.pos = start

    def moves(self):
        return [i for i in self.base.graph[self.pos]]

class BaseCriminal:
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

        self.our_criminal = CriminalStrategy(self)
        self.their_criminal = CriminalStrategy(self)
        self.student = StudentStrategy(self, begin)

    def output_current_vertex(self):
        return
        print("Student blob currently at", self.student.pos)
        print("Edges:")
        for v in self.graph[self.student.pos]:
            print((self.student.pos, v), "with initial weight", self.graph[self.student.pos][v], "total weight", self.graph[self.student.pos][v] + sum(p[0] for p in self.penalties[self.student.pos][v]))

    def minimax(self, is_criminal, is_ours, depth=0):
        if is_criminal:
            best_state = None
            criminal = self.our_criminal if is_ours else self.their_criminal

            for move in criminal.moves(self.student.pos):
                criminal.do_move(move, is_ours)

                # if is_ours:
                #     state = self.minimax(True, False, depth)
                # else:
                #     state = self.minimax(False, True, depth)
                state = self.minimax(False, True, depth)

                # Evaluations are viewed from the criminal so better score is
                # greater
                if best_state is None or state.better_for_criminal(best_state):
                    best_state = state
                    best_state.move = move

                criminal.undo_move(move)

            return best_state
        else:
            best_state = None

            for move in self.student.moves():
                current = self.student.pos
                criminal_score = self.score_multiplier * sum(p[0] for p in self.penalties[current][move] if p[1])
                student_weight = self.graph[current][move] + sum(p[0] for p in self.penalties[current][move])

                self.student.pos = move

                if depth == MINIMAX_DEPTH or move in self.targets:
                    # print(criminal_score, student_weight)
                    state = State(None, criminal_score, student_weight)
                else:
                    state = self.minimax(True, True, depth + 1)
                    state.score += criminal_score
                    state.weight += student_weight

                # An interesting observation is that due to the asymmetry of
                # the game and like the preexisting edge weights, the criminal
                # and student aren't exactly at odds at each other, but we'll
                # still say that in general the student looks to minimize the
                # criminal score.

                # Actually no we cannot make this assumption because then the
                # student just kills itself just to spite the criminal by going
                # to highly weighted edges
                if best_state is None or state.better_for_student(best_state):
                    best_state = state

                self.student.pos = current

            return best_state

    def strategy_prev(self, edge_updates, vertex_count, budget):
        # Use this to debug only the first move then stop
        # assert vertex_count[0] == 2
        self.our_criminal.budget = budget

        self.student_positions = vertex_count
        self.score_multiplier = 0

        for v in vertex_count:
            if vertex_count[v] > self.score_multiplier and v not in self.targets:
                self.score_multiplier = vertex_count[v]
                self.student.pos = v
                break

        # Just being safe surely this won't cause trouble surely right
        # assert self.score_multiplier > 0

        for update in edge_updates:
            # Okay some weird duplication is happening here so maybe fix it later by like removing the do move thing idk
            self.their_criminal.do_move((update[0], update[1], edge_updates[update]), False)

        # breakpoint()
        state = self.minimax(True, True)

        self.our_criminal.do_move(state.move, True)

        return state.move

    def strategy(self, edge_updates, vertex_count, budget):
        # Use this to debug only the first move then stop
        # assert vertex_count[0] == 2
        self.our_criminal.budget = budget

        # self.student_positions = vertex_count
        self.score_multiplier = 0

        for update in edge_updates:
            self.penalties[update[0]][update[1]].append((edge_updates[update], True))
            # self.their_criminal.do_move((update[0], update[1], edge_updates[update]), False)

        best_state = None

        # Okay like idt this is a bad thing to do but like hmmmmmmmmmm it's not
        # really working
        for v in vertex_count:
            if vertex_count[v] > 0 and v not in self.targets:
                self.score_multiplier = vertex_count[v]
                self.student.pos = v

                state = self.minimax(True, True)

                if best_state is None or state.better_for_criminal(best_state):
                    best_state = state

        # self.our_criminal.do_move(best_state.move, True)

        return best_state.move
