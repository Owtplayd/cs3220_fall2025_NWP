# src/pacman_multi_goal_agent.py
import random
from typing import List, Tuple, Set, Dict
from src.mazeProblemClass import MazeProblem
from src.heuristics import euclidean, manhattan
from src.search_algos import astar as _astar, ida_star as _ida
from src.nodeClass import Node


def reconstruct_path(n: Node) -> List[Tuple[int, int]]:
    return [x.state for x in n.path()]


def choose_next_food(current: Tuple[int, int], foods: Set[Tuple[int, int]], h):
    best, best_h = None, float("inf")
    for f in foods:
        val = h(current, f)
        if val < best_h:
            best, best_h = f, val
    return best


def place_ghosts(
    candidates: List[Tuple[int, int]], start, goal, foods: Set[Tuple[int, int]], k=5
):
    forbidden = set(foods) | {start, goal}
    pool = [s for s in candidates if s not in forbidden]
    random.shuffle(pool)
    return set(pool[:k])


def fight_outcome(perf_percent: float) -> bool:
    return perf_percent > 30.0


class PacmanPlanner:
    def __init__(
        self,
        graph,
        open_cells: List[Tuple[int, int]],
        start,
        goal,
        foods: Set[Tuple[int, int]],
        use_manhattan=False,
        use_idastar=False,
    ):
        self.graph = graph
        self.open_cells = open_cells
        self.start, self.goal = start, goal
        self.foods = set(foods)
        self.h = manhattan if use_manhattan else euclidean
        self.use_idastar = use_idastar

        self.performance_percent = 30.0
        self.total_cost = 0.0
        self.nodes_expanded = 0
        self.ghosts: Set[Tuple[int, int]] = set()
        self.segments: List[Dict] = []

    def _solve(self, s_from, s_to):
        prob = MazeProblem(s_from, s_to, self.graph)
        if self.use_idastar:
            node, stats = _ida(prob, self.h)
        else:
            node, stats = _astar(prob, self.h, want_stats=True)
        self.nodes_expanded += stats["expanded"]
        self.total_cost += stats["cost"]
        return node

    def _consume(self, path_states: List[Tuple[int, int]]):
        foods = set(self.foods)
        for s in path_states[1:]:
            if s in self.ghosts:
                if fight_outcome(self.performance_percent):
                    self.performance_percent -= self.performance_percent * 0.10
                else:
                    raise RuntimeError(f"Pac-Man was defeated by a ghost at {s}.")
            if s in foods:
                self.performance_percent *= 2.0
                foods.remove(s)
        self.foods = foods

    def build_plan(self):
        # place 5 ghosts
        self.ghosts = place_ghosts(
            self.open_cells, self.start, self.goal, self.foods, k=5
        )
        current = self.start
        colors = ["#f4d03f", "#58d68d", "#5dade2", "#af7ac5", "#ec7063"]
        ci = 0

        while self.foods:
            nxt = choose_next_food(current, self.foods, self.h)
            node = self._solve(current, nxt)
            if node is None:
                raise RuntimeError(f"No path {current}->{nxt}")
            path_states = reconstruct_path(node)
            self._consume(path_states)
            self.segments.append(
                {
                    "from": current,
                    "to": nxt,
                    "path": path_states,
                    "color": colors[ci % len(colors)],
                }
            )
            ci += 1
            current = nxt

        node = self._solve(current, self.goal)
        if node is None:
            raise RuntimeError(f"No path {current}->{self.goal}")
        path_states = reconstruct_path(node)
        self._consume(path_states)
        self.segments.append(
            {
                "from": current,
                "to": self.goal,
                "path": path_states,
                "color": colors[ci % len(colors)],
            }
        )

        return {
            "segments": self.segments,
            "nodes_expanded": self.nodes_expanded,
            "total_cost": self.total_cost,
            "final_performance_percent": self.performance_percent,
            "ghosts": list(self.ghosts),
        }
