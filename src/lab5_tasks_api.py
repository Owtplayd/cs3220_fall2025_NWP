# src/lab5_tasks_api.py
# ---------------------------------------------------------------------
# Thin wrappers for Lab 5 tasks. Heuristics are imported from the
# local search module (not from a heuristics.py file).
# ---------------------------------------------------------------------

from __future__ import annotations
from typing import List, Tuple
from src.mazeProblemClass import MazeProblem
from src.maze2025GraphClass import mazeGraph

from src.informed_search_ext import (
    astar_euclidean,
    astar_manhattan,
    ida_star,
    make_multigoal_heuristic,
    make_multigoal_heuristic_mst,
    manhattan,
)
from src.pacman_world_ext import PacmanEnvironment

State = Tuple[int, int]


def task1_astar_euclidean(initial: State, goal: State, g: mazeGraph):
    problem = MazeProblem(initial, goal, g)
    return astar_euclidean(problem)


def task2_astar_manhattan(initial: State, goal: State, g: mazeGraph):
    problem = MazeProblem(initial, goal, g)
    return astar_manhattan(problem)


def task3_build_world(
    g: mazeGraph,
    start: State,
    goal: State,
    food_ratio: float = 0.10,
    num_ghosts: int = 5,
    seed: int | None = None,
):
    return PacmanEnvironment(
        g, start, goal, food_ratio=food_ratio, num_ghosts=num_ghosts, seed=seed
    )


def task4_make_multigoal_heuristic(
    foods: List[State], final_goal: State, use_mst: bool = False
):
    return (
        make_multigoal_heuristic_mst(foods, final_goal)
        if use_mst
        else make_multigoal_heuristic(foods, final_goal)
    )


def task6_idastar_run(initial: State, goal: State, g: mazeGraph, heuristic=None):
    problem = MazeProblem(initial, goal, g)
    if heuristic is None:
        heuristic = lambda s: manhattan(s, goal)
    return ida_star(problem, heuristic)
