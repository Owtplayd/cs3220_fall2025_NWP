# src/asteroidData.py
# Asteroid Maze generator + domain helpers for Satellite task.
# Grid: 0=asteroid (blocked), 1=free. Enemies occupy some free cells.

from __future__ import annotations
import numpy as np
from typing import Dict, Tuple, List, Set

Coord = Tuple[int, int]

# Action encoding required by the task
LEFT, UP, RIGHT, DOWN = 0, 1, 2, 3
ACTION_NAMES = {
    LEFT: "left",
    UP: "up",
    RIGHT: "right",
    DOWN: "down",
}
# Direction vectors
DIRS = {
    LEFT: (0, -1),
    UP: (-1, 0),
    RIGHT: (0, 1),
    DOWN: (1, 0),
}

# Non-uniform action costs (per spec)
ACTION_COST = {
    LEFT: 2,
    RIGHT: 2,
    DOWN: 1,
    UP: 4,
}


def generate_asteroid_grid(
    n: int = 7, asteroid_ratio: float = 0.25, seed: int | None = None
) -> np.ndarray:
    """
    Create an n×n grid with 0=asteroid, 1=free. About asteroid_ratio cells are 0.
    Ensures at least one free cell for S and one for G.
    """
    if seed is not None:
        np.random.seed(int(seed))
    # Bernoulli draw -> many small obstacles (simple & reproducible)
    grid = (np.random.rand(n, n) > asteroid_ratio).astype(int)

    # Force at least two free cells (start & goal)
    grid[0, 0] = 1
    grid[n - 1, n - 1] = 1
    return grid


def place_enemies(
    grid: np.ndarray, enemy_ratio: float = 0.10, seed: int | None = None
) -> Dict[Coord, int]:
    """
    Place enemies on *free* cells (1). Return dict: {coord: power}.
    Power in [10%, 40%] of N (N = number of free nodes in state-space).
    """
    if seed is not None:
        np.random.seed(int(seed) + 1337)

    free_cells = [
        (i, j)
        for i in range(grid.shape[0])
        for j in range(grid.shape[1])
        if grid[i, j] == 1
    ]
    N = len(free_cells)
    k = max(1, int(round(enemy_ratio * N)))  # at least 1 enemy if any free cells exist
    choices = np.random.choice(
        len(free_cells), size=min(k, len(free_cells)), replace=False
    )

    enemies: Dict[Coord, int] = {}
    lo, hi = max(1, int(0.10 * N)), max(1, int(0.40 * N))
    for idx in choices:
        coord = tuple(free_cells[idx])
        power = int(np.random.randint(lo, hi + 1))
        enemies[coord] = power
    return enemies


def start_goal(grid: np.ndarray) -> Tuple[Coord, Coord]:
    """Pick S=(0,0), G=(n-1,n-1) but ensure both are free; otherwise move to nearest free cell."""
    n = grid.shape[0]
    S = (0, 0)
    G = (n - 1, n - 1)
    if grid[S] == 0:
        S = _nearest_free(grid, S)
    if grid[G] == 0:
        G = _nearest_free(grid, G)
    return S, G


def _nearest_free(grid: np.ndarray, where: Coord) -> Coord:
    """BFS in the grid to find nearest free (1) cell from 'where'."""
    n = grid.shape[0]
    from collections import deque

    q = deque([where])
    seen = {where}
    while q:
        i, j = q.popleft()
        if 0 <= i < n and 0 <= j < n and grid[i, j] == 1:
            return (i, j)
        for di, dj in DIRS.values():
            ni, nj = i + di, j + dj
            if 0 <= ni < n and 0 <= nj < n and (ni, nj) not in seen:
                seen.add((ni, nj))
                q.append((ni, nj))
    # Fallback
    return (0, 0)


def define_actions(grid: np.ndarray) -> Dict[Coord, List[int]]:
    """For each free cell, list legal encoded actions (0..3) that remain on free cells."""
    n = grid.shape[0]
    actions: Dict[Coord, List[int]] = {}
    for i in range(n):
        for j in range(n):
            if grid[i, j] != 1:
                continue
            avail: List[int] = []
            for a, (di, dj) in DIRS.items():
                ni, nj = i + di, j + dj
                if 0 <= ni < n and 0 <= nj < n and grid[ni, nj] == 1:
                    avail.append(a)
            actions[(i, j)] = avail
    return actions


def make_transition_model(
    actions: Dict[Coord, List[int]],
) -> Dict[Coord, Dict[int, Coord]]:
    """{state: {action_code: next_state}}."""
    origin: Dict[Coord, Dict[int, Coord]] = {}
    for s, acts in actions.items():
        i, j = s
        origin[s] = {}
        for a in acts:
            di, dj = DIRS[a]
            origin[s][a] = (i + di, j + dj)
    return origin


def initial_performance(grid: np.ndarray) -> int:
    """Initial perf = 50% of number of nodes in the state space (free cells)."""
    N = int((grid == 1).sum())
    return max(1, int(round(0.5 * N)))
