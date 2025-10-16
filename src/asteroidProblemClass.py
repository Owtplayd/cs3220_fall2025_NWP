# src/asteroidProblemClass.py
# Problem wrapper for Asteroid Maze with non-uniform costs.
from __future__ import annotations
from typing import Dict, Tuple
from src.problemClass import Problem  # your base Problem API (actions, result, etc.)
from data.asteroidData import ACTION_COST, ACTION_NAMES

Coord = Tuple[int, int]


class AsteroidProblem(Problem):
    """
    State = (i,j)
    Actions(state) -> iterable of encoded actions (0..3)
    Result(state, action) -> neighbor (i2,j2)
    Goal_test(state) -> state == goal
    path_cost accumulates non-uniform ACTION_COST
    """

    def __init__(
        self, initial: Coord, goal: Coord, origin: Dict[Coord, Dict[int, Coord]]
    ):
        self.initial = initial
        self.goal = goal
        self.origin = origin  # {state: {action: next_state}}

    def actions(self, state: Coord):
        return self.origin.get(state, {}).keys()

    def result(self, state: Coord, action: int):
        return self.origin[state][action]

    def goal_test(self, state: Coord):
        return state == self.goal

    def path_cost(self, c, state1, action, state2):
        # c = current cumulative cost
        return c + ACTION_COST[action]

    # Optional pretty action string (useful for logs)
    def action_name(self, action: int) -> str:
        return ACTION_NAMES.get(action, str(action))
