"""
Edit this file! This is the file you will submit.
"""

import random

"""
NOTE: Each soldier's memory in the final runner will be separate from the others.

WARNING: Do not print anything to stdout. It will break the grading script!
"""

def strategy(ally: list, enemy: list, offset: int) -> int:
    # gravitate to tower - very simplistic
    return offset

def strategy_heuristic_old(ally: list, enemy: list, offset: int) -> int:
    defense = 0.3
    # primarily, gravitate to tower, however, if a tower is already full then
    # offload some acceptable amount of soldiers to distribute
    if offset == 0:
        # if tower already holds majority then offload
        if random.random() < (ally[3] - enemy[3] -1 -
                (enemy[2]+enemy[4])*defense)/ally[3]:
            return 1 if random.random() > .5 else -1
        return 0
    # if closest tower needs allies gravitate
    if enemy[3+offset] > ally[3+offset]:
        if random.random() < (enemy[3+offset] - ally[3+offset] + 1)/ally[3]:
            return offset
    # if farther tower needs allies gravitate
    if enemy[3-offset*2] > ally[3-offset*2]:
        if random.random() < (enemy[3+offset*2] - ally[3+offset*2] + 1)/ally[3]:
            return -offset
    # randomwalk
    return random.randint(-1, 1)

def bad_strategy(ally: list, enemy: list, offset: int) -> int:
    # A bad strategy to use in your game
    return 1 if offset == 0 else -offset

def random_strategy(ally: list, enemy: list, offset: int) -> int:
    # A random strategy to use in your game
    return random.randint(-1, 1)

stat = 0
oa = 0
oe = 0
jl = False
dr = 0

def strategy_heuristic(ally: list, enemy: list, offset: int) -> int:
    global stat, oa, oe, jl, dr
    if dr != 0:
        if offset == 0: dr = 0
        else: return dr
    defense = 3
    sac = 1.8
    if stat > 5: sac = 1
    # primarily, gravitate to tower, however, if a tower is already full then
    # offload some acceptable amount of soldiers to distribute
    if offset == 0:
        jl = False
        # triage
#        if enemy[3] > ally[3] * sac:
        if enemy[3] > ally[2] + ally[3] + ally[4]:
            stat = 0
            jl = True
            dr = 1 if random.random() > .5 else -1
            return dr
        # if tower already holds majority then offload
        if random.random() < (ally[3] - enemy[3] -1 -
                (enemy[2]+enemy[4])*defense)/ally[3]:
            stat = 0
            return 1 if random.random() > .5 else -1
        if oa == ally[3] and oe == enemy[3]: stat += 1
        else: stat = 0
        oa = ally[3]
        oe = enemy[3]
        return 0
    stat = 0
    # if closest tower needs allies gravitate
    if enemy[3+offset] > ally[3+offset] and not jl:
        if random.random() < (enemy[3+offset] - ally[3+offset] + 1)/ally[3]:
            return offset
    jl = False
    # if farther tower needs allies gravitate
    if enemy[3-offset*2] > ally[3-offset*2]:
        if random.random() < (enemy[3+offset*2] - ally[3+offset*2] + 1)/ally[3]:
            return -offset
    # randomwalk
    return random.randint(-1, 1)

def bad_strategy(ally: list, enemy: list, offset: int) -> int:
    # A bad strategy to use in your game
    return 1 if offset == 0 else -offset

def random_strategy(ally: list, enemy: list, offset: int) -> int:
    # A random strategy to use in your game
    return random.randint(-1, 1)


def get_strategies():
    """
    Returns a list of strategies to play against each other.

    In the local tester, all of the strategies will be used as separate players, and the 
    pairwise winrate will be calculated for each strategy.

    In the official grader, only the first element of the list will be used as your strategy.
    """
    strategies = [strategy_heuristic, strategy_heuristic_old, strategy]

    return strategies
