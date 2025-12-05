from collections import defaultdict, Counter
import random


class UniversalDict:
    """A universal dict maps any key to the same value. 
    We use it here as the domains dict for CSPs 
    in which all variables have the same domain.
    >>> d = UniversalDict(list('RGB'))
    >>> d['SA']
    ['R','G','B']
    """

    def __init__(self, value): 
      self.value = value

    def __getitem__(self, key): 
      return self.value

    def __repr__(self): 
      return f'Any from {self.value}'


def different_values_constraint(A, a, B, b):
    """A constraint saying two neighboring variables must differ in value."""
    return a != b



def parse_neighbors(neighbors):
    """Convert a string of the form 'X: Y Z; Y: Z' into a dict mapping
    regions to neighbors. The syntax is a region name followed by a ':'
    followed by zero or more region names, followed by ';', repeated for
    each region name. If you say 'X: Y' you don't need 'Y: X'.
    >>> parse_neighbors('X: Y Z; Y: Z') == {'Y': ['X', 'Z'], 'X': ['Y', 'Z'], 'Z': ['X', 'Y']}
    True
    """
    dic = defaultdict(list)
    specs = [spec.split(':') for spec in neighbors.split(';')]
    for (A, Aneighbors) in specs:
        #print(A)
        A = A.strip()
        for B in Aneighbors.split():
            dic[A].append(B)
            dic[B].append(A)
    return dic


def count(seq):
    """Count the number of items in sequence that are interpreted as true."""
    return sum(map(bool, seq))

def first(iterable, default=None):
    """Return the first element of an iterable; or default."""
    return next(iter(iterable), default)





def min_conflicts_value1(csp, var, current):
    """Return the value that will give var the least number of conflicts.
    If there is a tie, choose at random."""
    print(f"var {var} (val, nConflicts):")
    varConflicts=[(val,csp.nconflicts(var, val, current)) for val in csp.domains[var]]
    print(f"{varConflicts}")
    return argmin_random_tie(csp.domains[var], key=lambda val: csp.nconflicts(var, val, current))

def argmin_random_tie(seq, key):
    """Return a minimum element of seq; break ties at random."""
    minElem=min(shuffled(seq), key=key)
    print(f"The value {minElem} -> selected")
    return minElem

def shuffled(iterable):
    """Randomly shuffle a copy of iterable."""
    items = list(iterable)
    random.shuffle(items)
    return items


