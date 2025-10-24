# src/pacman_world_ext.py
# ---------------------------------------------------------------------
# Pac-Man world helpers for Lab 5 (foods, ghosts, performance rules).
# Does NOT modify existing modules. Composes your Graph/MazeProblem.
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
    Standalone environment for Lab 5 extensions:
      - randomly place fixed foods (10% of cells)
      - randomly place 5 ghosts (not on start/finish or food; unique)
      - manage performance dynamics and ghost encounters
    It does NOT alter your existing Environment or Navigation classes.
    """

    def __init__(self, graph: mazeGraph, start: State, goal: State, food_ratio: float = 0.10, num_ghosts: int = 5, seed: Optional[int] = None):
        super().__init__()
        self.graph = graph
        self.start = start
        self.goal = goal
        self.food_ratio = food_ratio
        self.num_ghosts = num_ghosts
        self.rng = random.Random(seed)

        nodes = [n for n in self.graph.nodes() if isinstance(n, tuple) and len(n) == 2]
        self.all_cells: List[State] = nodes

        # Place foods
        k = max(1, int(len(self.all_cells) * self.food_ratio))
        illegal_for_food = set()  # could add walls if needed; graph.nodes() already excludes walls
        candidates = [c for c in self.all_cells if c not in illegal_for_food]
        self.foods: Set[State] = set(self.rng.sample(candidates, k=min(k, len(candidates))))
        # Start/goal may also have food per spec (so do not exclude them).

        # Place ghosts
        forbidden = set(self.foods) | {self.start, self.goal}
        g_candidates = [c for c in self.all_cells if c not in forbidden]
        chosen = self.rng.sample(g_candidates, k=min(self.num_ghosts, len(g_candidates)))
        self.ghosts: List[Ghost] = [Ghost(i, pos) for i, pos in enumerate(chosen, start=1)]

        # Performance rules
        self.total_cells = len(self.all_cells)
        self.performance = int(0.30 * self.total_cells)  # 30% of cells
        self.alive = True

    # -------------------------- API helpers -----------------------------

    def has_food(self, s: State) -> bool:
        return s in self.foods

    def eat_food(self, s: State) -> None:
        if s in self.foods:
            self.foods.remove(s)
            # After eating a food dot -> performance doubles
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
        # Encounter rule
        thresh = int(0.30 * self.total_cells)
        if self.performance > thresh:
            # Wins but loses 10% of previous effectiveness
            loss = max(1, int(round(self.performance * 0.10)))
            self.performance = max(0, self.performance - loss)
            # Remove ghost from world after defeat
            self.ghosts = [gh for gh in self.ghosts if gh.pos != s]
        else:
            # Dies
            self.alive = False

    # --------------------- Convenience run utilities --------------------

    def simulate_path(self, path: List[State]) -> dict:
        """
        Walk a path of states, applying food and ghost rules.
        Returns a report dict of the run.
        """
        report = {
            "start": self.start,
            "goal": self.goal,
            "final_state": None,
            "alive": True,
            "performance": self.performance,
            "foods_eaten": 0,
            "foods_remaining": len(self.foods),
            "ghosts_remaining": len(self.ghosts),
            "events": [],  # list of (state, event_str)
        }
        cur_perf = self.performance
        foods_eaten = 0

        for s in path:
            # Eat food first (can be at start/goal as well)
            if self.has_food(s):
                self.eat_food(s)
                foods_eaten += 1
                report["events"].append((s, "ate_food -> performance_doubled"))
            # Check ghost encounter
            before_alive = self.alive
            self.meet_ghost(s)
            if not self.alive and before_alive:
                report["events"].append((s, "met_ghost -> died"))
                report["final_state"] = s
                break
            elif before_alive and self.alive and self.ghost_at(s) is None:
                # if the ghost was there, meet_ghost would remove it and add event above
                pass
            elif before_alive and self.alive:
                report["events"].append((s, "met_ghost -> won_but_lost_10_percent"))

        report["final_state"] = report["final_state"] or (path[-1] if path else self.start)
        report["alive"] = self.alive
        report["performance"] = self.performance
        report["foods_eaten"] = foods_eaten
        report["foods_remaining"] = len(self.foods)
        report["ghosts_remaining"] = len(self.ghosts)
        return report
