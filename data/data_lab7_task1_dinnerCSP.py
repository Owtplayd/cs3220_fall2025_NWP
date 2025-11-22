# ==========================================================
# data/data_lab7_task1_dinnerCSP.py
# Data file for Lab 7 – Task 1 (Dinner Accommodation CSP)
# ==========================================================

from src.CSPclass import CSP
from src.utils import UniversalDict

# 6 chairs around a round table
CHAIRS = [f"Seat{i}" for i in range(6)]

# Five colleagues + one empty chair
PEOPLE = ["A", "B", "C", "D", "E", "Empty"]

# Adjacent chairs in the circle (Seat0-Seat1-...-Seat5-Seat0)
ADJACENT_PAIRS = set()
for i in range(len(CHAIRS)):
    a = CHAIRS[i]
    b = CHAIRS[(i + 1) % len(CHAIRS)]
    ADJACENT_PAIRS.add((a, b))
    ADJACENT_PAIRS.add((b, a))


def dinner_constraint(X, x, Y, y):
    """
    Binary constraint for the dinner CSP.

    Global all-different:
      no person (or Empty) can appear in two different chairs.

    Local neighbor constraints (only for adjacent chairs X,Y):
      - A not next to B
      - B not next to E
      - B not next to C
    """
    # all-different
    if x == y:
        return False

    # local adjacency constraints
    if (X, Y) in ADJACENT_PAIRS:
        pair = {x, y}
        if {"A", "B"} == pair:
            return False
        if {"B", "E"} == pair:
            return False
        if {"B", "C"} == pair:
            return False

    return True


def make_dinner_csp():
    """
    Construct and return a CSP instance representing the
    Dinner Accommodation Problem.
    """
    # same domain for every chair
    domains = UniversalDict(PEOPLE)

    # neighbors: complete graph on chairs (for all-different)
    neighbors = {seat: [other for other in CHAIRS if other != seat] for seat in CHAIRS}

    dinner_csp = CSP(
        variables=list(CHAIRS),
        domains=domains,
        neighbors=neighbors,
        constraints=dinner_constraint,
    )
    return dinner_csp
