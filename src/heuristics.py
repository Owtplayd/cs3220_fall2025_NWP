# src/heuristics.py
from math import sqrt


def euclidean(a, b):
    (r1, c1), (r2, c2) = a, b
    return sqrt((r1 - r2) ** 2 + (c1 - c2) ** 2)


def manhattan(a, b):
    (r1, c1), (r2, c2) = a, b
    return abs(r1 - r2) + abs(c1 - c2)
