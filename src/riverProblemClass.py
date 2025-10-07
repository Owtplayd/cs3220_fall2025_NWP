# src/riverProblemClass.py
from src.problemClass import Problem

LEFT = "L"
RIGHT = "R"


# State = (F, W, G, C)
class RiverProblem(Problem):
    def __init__(
        self,
        initial=(LEFT, LEFT, LEFT, LEFT),
        goal=(RIGHT, RIGHT, RIGHT, RIGHT),
        cost_version="1.0",
    ):
        super().__init__(initial, goal)
        assert cost_version in ("1.0", "1.01")
        self.cost_version = cost_version

    # -------- helpers --------
    def _is_safe(self, state):
        f, w, g, c = state
        if f != w and w == g:
            return False  # wolf with goat without farmer
        if f != g and g == c:
            return False  # goat with cabbage without farmer
        return True

    def _flip(self, side):
        return RIGHT if side == LEFT else LEFT

    # Actions: 'F', 'FW', 'FG', 'FC'
    def actions(self, state):
        f, w, g, c = state
        actions = []

        # Farmer alone
        cand = self.result(state, "F")
        if cand and self._is_safe(cand):
            actions.append("F")

        # With wolf
        if f == w:
            cand = self.result(state, "FW")
            if cand and self._is_safe(cand):
                actions.append("FW")

        # With goat
        if f == g:
            cand = self.result(state, "FG")
            if cand and self._is_safe(cand):
                actions.append("FG")

        # With cabbage
        if f == c:
            cand = self.result(state, "FC")
            if cand and self._is_safe(cand):
                actions.append("FC")

        return actions

    def result(self, state, action):
        f, w, g, c = state
        if action == "F":
            nf = self._flip(f)
            new_state = (nf, w, g, c)
        elif action == "FW" and f == w:
            nf = self._flip(f)
            new_state = (nf, self._flip(w), g, c)
        elif action == "FG" and f == g:
            nf = self._flip(f)
            new_state = (nf, w, self._flip(g), c)
        elif action == "FC" and f == c:
            nf = self._flip(f)
            new_state = (nf, w, g, self._flip(c))
        else:
            return None

        return new_state if self._is_safe(new_state) else None

    def path_cost(self, c, state1, action, state2):
        if self.cost_version == "1.0":
            return c + 1
        # Version 1.01: weighted crossings (see assignment)
        if action == "F":
            k = 1
        elif action == "FC":
            k = 2
        else:  # 'FW' or 'FG'
            k = 3
        return c + k
