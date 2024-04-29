"""
Edit this file! This is the file you will submit.
"""

import random

"""
NOTE: Each soldier's memory in the final runner will be separate from the others.

WARNING: Do not print anything to stdout. It will break the grading script!
"""

bias = 0

def strategy_heuristic(ally: list, enemy: list, offset: int) -> int:
    global bias
    spon = 1
    if bias != 0:
        if offset == bias:
            if random.random() < (enemy[3+offset] - ally[3+offset] + 1)/ally[3]:
                bias = 0
                return offset
        if offset == 0:
            if random.random() < spon:
                bias = 0
        return bias
    if offset == 0:
        defense = 0.7
        if enemy[3] + defense*(enemy[2] + enemy[4]) < ally[3]:
            if random.random() < (ally[3] - enemy[3] - defense*(enemy[2] + enemy[4]) - 2)/ally[3]:
                return 1 if random.random() < 0.5 else -1
            return 0
        if enemy[3] + defense*(enemy[2] + enemy[4]) > ally[3] + ally[2] + ally[4] + ally[1] + ally[5]:
            bias = 1 if random.random() < 0.5 else -1
            return bias
        return 0
    # if closest tower needs allies gravitate
    if enemy[3+offset] >= ally[3+offset]:
        if random.random() < (enemy[3+offset] - ally[3+offset] + 1)/ally[3]:
            return offset
    # if farther tower needs allies gravitate
    if enemy[3-offset*2] >= ally[3-offset*2]:
        if random.random() < (enemy[3+offset*2] - ally[3+offset*2] + 1)/ally[3]:
            return -offset
    # randomwalk
    return 1 if random.random() < 0.5 else -1

def get_strategies():
    """
    Returns a list of strategies to play against each other.

    In the local tester, all of the strategies will be used as separate players, and the 
    pairwise winrate will be calculated for each strategy.

    In the official grader, only the first element of the list will be used as your strategy.
    """
    strategies = [strategy_heuristic]

    return strategies
