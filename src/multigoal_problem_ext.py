# src/multigoal_problem_ext.py
# ---------------------------------------------------------------------
# Multi-goal Maze Problem (state = (pos, frozenset(remaining_foods))).
# No heuristics imports here; this class is purely the Problem dynamics.
# ---------------------------------------------------------------------

from __future__ import annotations
from typing import Set, Tuple, FrozenSet
from src.problemClass import Problem

Pos = Tuple[int, int]
StateMG = Tuple[Pos, FrozenSet[Pos]]


class MultiGoalMazeProblem(Problem):
    """
    Graph interface expected:
      - graph.origin[pos] -> dict(action -> next_pos)
      - graph.get(pos, next_pos) -> edge cost (default 1 if None)
    Goal: remaining_foods == ∅ and pos == finish
    """

    def __init__(self, initial_pos: Pos, finish: Pos, foods: Set[Pos], graph):
        initial_state: StateMG = (initial_pos, frozenset(foods))
        super().__init__(initial_state, finish)
        self.finish: Pos = finish
        self.graph = graph

    def actions(self, state: StateMG):
        pos, _ = state
        return list(self.graph.origin[pos].keys())

    def result(self, state: StateMG, action) -> StateMG:
        pos, remaining = state
        next_pos = self.graph.origin[pos][action]
        if next_pos in remaining:
            remaining = frozenset([f for f in remaining if f != next_pos])
        return (next_pos, remaining)

    def goal_test(self, state: StateMG) -> bool:
        pos, remaining = state
        return (pos == self.finish) and (len(remaining) == 0)

    def path_cost(
        self, cost_so_far: float, state: StateMG, action, next_state: StateMG
    ) -> float:
        pos, _ = state
        next_pos, _ = next_state
        step = self.graph.get(pos, next_pos)
        return cost_so_far + (step if step is not None else 1.0)
