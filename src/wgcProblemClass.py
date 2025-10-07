# src/wgcProblemClass.py
from src.problemClass import Problem


def other_side(side: str) -> str:
    return "R" if side == "L" else "L"


class WGCProblem(Problem):
    """
    Wolf–Goat–Cabbage river crossing as a search problem.

    State: tuple(F, W, G, C) where each is 'L' or 'R' (left/right bank).
           F is the Farmer (and boat).
    Actions: 'F'  (farmer rows alone),
             'FW' (farmer rows with Wolf),
             'FG' (farmer rows with Goat),
             'FC' (farmer rows with Cabbage).
    Constraints: Never leave Wolf with Goat or Goat with Cabbage on a bank
                 without the Farmer.
    Costs:
      cost_mode='v1'    -> every crossing costs 1
      cost_mode='v1.01' -> boat move (1) + handling: Cabbage(+2), Wolf/Goat(+3), Alone(+0)
    """

    ACTIONS = ("F", "FW", "FG", "FC")

    def __init__(
        self, initial=("L", "L", "L", "L"), goal=("R", "R", "R", "R"), cost_mode="v1"
    ):
        super().__init__(initial=initial, goal=goal)
        assert cost_mode in ("v1", "v1.01"), "cost_mode must be 'v1' or 'v1.01'"
        self.cost_mode = cost_mode

    def actions(self, state):
        f, w, g, c = state
        candidates = ["F"]
        if w == f:
            candidates.append("FW")
        if g == f:
            candidates.append("FG")
        if c == f:
            candidates.append("FC")

        legal = []
        for a in candidates:
            ns = self.result(state, a)
            if self._is_safe(ns):
                legal.append(a)
        return legal

    def result(self, state, action):
        f, w, g, c = state
        nf = other_side(f)
        nw, ng, nc = w, g, c
        if action == "FW":
            nw = other_side(w)
        elif action == "FG":
            ng = other_side(g)
        elif action == "FC":
            nc = other_side(c)
        elif action != "F":
            raise ValueError(f"Unknown action {action}")
        return (nf, nw, ng, nc)

    def goal_test(self, state):
        return super().goal_test(state)

    def path_cost(self, c, state1, action, state2):
        if self.cost_mode == "v1":
            return c + 1
        add = 1  # boat move
        if action == "FC":
            add += 2
        elif action in ("FW", "FG"):
            add += 3
        elif action == "F":
            add += 0
        return c + add

    @staticmethod
    def _is_safe(state):
        f, w, g, c = state
        for side in ("L", "R"):
            farmer = f == side
            wolf = w == side
            goat = g == side
            cab = c == side
            if (not farmer) and ((wolf and goat) or (goat and cab)):
                return False
        return True
