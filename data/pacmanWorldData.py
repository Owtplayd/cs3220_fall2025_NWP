# data/PacmanWorldData.py

from typing import List, Tuple, Set, Dict
from random import Random

SEED: int = 3220  # deterministic world; change to reshuffle
FOOD_RATIO: float = 0.10  # 10% of space cells are food (2)
GHOST_COUNT: int = 5  # number of hidden ghosts
ALLOW_FOOD_ON_START: bool = True
ALLOW_FOOD_ON_GOAL: bool = True

# Heuristic / search choices (read by your runner)
USE_MANHATTAN: bool = True  # False => Euclidean
USE_IDASTAR: bool = False  # True => IDA* instead of A* for planning legs


# Minimal helpers


def derive_world(
    maze_matrix: List[List[int]],
    start: Tuple[int, int],
    goal: Tuple[int, int],
) -> Dict[str, object]:
    """
    Given a 2D maze matrix (0=wall, 1=open, 2=food), a start and a goal:
      - randomly add FOOD (2) to ~10% of open cells (optionally including start/goal)
      - randomly place GHOSTS (not on start, not on goal, and not on food)
    Returns a dict with `foods`, `ghosts`, and `open_cells`.
    Assumes inputs are valid; intentionally no extra checks.
    """
    rng = Random(SEED)

    rows, cols = len(maze_matrix), len(maze_matrix[0])
    open_cells = [
        (r, c) for r in range(rows) for c in range(cols) if maze_matrix[r][c] != 0
    ]

    # Food candidates
    food_candidates = []
    for rc in open_cells:
        if rc == start and not ALLOW_FOOD_ON_START:
            continue
        if rc == goal and not ALLOW_FOOD_ON_GOAL:
            continue
        food_candidates.append(rc)

    target_food_count = max(1, int(round(len(open_cells) * FOOD_RATIO)))
    rng.shuffle(food_candidates)
    foods: Set[Tuple[int, int]] = set(food_candidates[:target_food_count])

    # Reflect food into matrix (value 2) without checks
    for r, c in foods:
        maze_matrix[r][c] = 2

    # Ghosts: not on start, not on goal, not on food
    forbidden = set(foods) | {start, goal}
    ghost_candidates = [rc for rc in open_cells if rc not in forbidden]
    rng.shuffle(ghost_candidates)
    ghosts: Set[Tuple[int, int]] = set(ghost_candidates[:GHOST_COUNT])

    return {
        "foods": foods,
        "ghosts": ghosts,
        "open_cells": open_cells,
        "seed": SEED,
        "food_ratio": FOOD_RATIO,
        "ghost_count": GHOST_COUNT,
        "use_manhattan": USE_MANHATTAN,
        "use_idastar": USE_IDASTAR,
    }
