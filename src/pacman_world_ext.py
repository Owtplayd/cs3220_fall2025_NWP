# src/pacman_world_ext.py
# ---------------------------------------------------------------------
# Pac-Man world helpers for Lab 5 (foods, ghosts, performance rules).
# No external heuristics imports; this module is independent.
# ---------------------------------------------------------------------

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Set, Tuple, Optional
import random

from src.environmentClass import Environment
from src.maze2025GraphClass import mazeGraph

State = Tuple[int, int]


@dataclass(frozen=True)
class Ghost:
    id: int
    pos: State


class PacmanEnvironment(Environment):
    """
    - Place ~10% foods (green), allow food on start/goal.
    - Place 5 ghosts (red), not on start/goal/food, unique positions.
    - Performance rules:
        * start = 30% of #nodes
        * eat food -> performance doubles (capped at #nodes)
        * meet ghost:
            - if performance > 30% -> win, lose 10% of previous effectiveness
            - else -> die
    """

    def __init__(
        self,
        graph: mazeGraph,
        start: State,
        goal: State,
        food_ratio: float = 0.10,
        num_ghosts: int = 5,
        seed: Optional[int] = None,
    ):
        super().__init__()
        self.graph = graph
        self.start = start
        self.goal = goal
        self.food_ratio = food_ratio
        self.num_ghosts = num_ghosts
        self.rng = random.Random(seed)

        nodes = [n for n in self.graph.nodes() if isinstance(n, tuple) and len(n) == 2]
        self.all_cells: List[State] = nodes

        k = max(1, int(len(self.all_cells) * self.food_ratio))
        candidates = list(self.all_cells)
        self.foods: Set[State] = set(
            self.rng.sample(candidates, k=min(k, len(candidates)))
        )
        # Start/goal can have food per spec.

        forbidden = set(self.foods) | {self.start, self.goal}
        g_candidates = [c for c in self.all_cells if c not in forbidden]
        chosen = self.rng.sample(
            g_candidates, k=min(self.num_ghosts, len(g_candidates))
        )
        self.ghosts: List[Ghost] = [
            Ghost(i, pos) for i, pos in enumerate(chosen, start=1)
        ]

        self.total_cells = len(self.all_cells)
        self.performance = int(0.30 * self.total_cells)
        self.alive = True

    # --- queries & transitions ---

    def has_food(self, s: State) -> bool:
        return s in self.foods

    def eat_food(self, s: State) -> None:
        if s in self.foods:
            self.foods.remove(s)
            self.performance = min(self.total_cells, self.performance * 2)

    def ghost_at(self, s: State) -> Ghost | None:
        for g in self.ghosts:
            if g.pos == s:
                return g
        return None

    def meet_ghost(self, s: State) -> None:
        g = self.ghost_at(s)
        if g is None:
            return
        thresh = int(0.30 * self.total_cells)
        if self.performance > thresh:
            loss = max(1, int(round(self.performance * 0.10)))
            self.performance = max(0, self.performance - loss)
            self.ghosts = [gh for gh in self.ghosts if gh.pos != s]
        else:
            self.alive = False

    def simulate_path(self, path: List[State]) -> dict:
        report = {
            "start": self.start,
            "goal": self.goal,
            "final_state": None,
            "alive": True,
            "performance": self.performance,
            "foods_eaten": 0,
            "foods_remaining": len(self.foods),
            "ghosts_remaining": len(self.ghosts),
            "events": [],
        }
        foods_eaten = 0

        for s in path:
            if self.has_food(s):
                self.eat_food(s)
                foods_eaten += 1
                report["events"].append((s, "ate_food -> performance_doubled"))
            was_alive = self.alive
            self.meet_ghost(s)
            if was_alive and not self.alive:
                report["events"].append((s, "met_ghost -> died"))
                report["final_state"] = s
                break
            elif was_alive and self.alive and self.ghost_at(s) is None:
                pass
            elif was_alive and self.alive:
                report["events"].append((s, "met_ghost -> won_but_lost_10_percent"))

        report["final_state"] = report["final_state"] or (
            path[-1] if path else self.start
        )
        report["alive"] = self.alive
        report["performance"] = self.performance
        report["foods_eaten"] = foods_eaten
        report["foods_remaining"] = len(self.foods)
        report["ghosts_remaining"] = len(self.ghosts)
        return report
