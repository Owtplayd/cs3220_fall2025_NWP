# ==========================================================
# data_lab6_task2_asteriskSudokuCSP.py
# Data file for Lab 6 – Task 2 (Asterisk Sudoku CSP)
# ==========================================================

from src.CSPclass import CSP

ROWS = "ABCDEFGHI"
COLS = "123456789"


def cross(A, B):
    return [a + b for a in A for b in B]


ASTERISK_CELLS = [
    "B5",
    "C3",
    "C7",
    "E1",
    "E5",
    "E9",
    "G3",
    "G7",
    "H5",
]

GIVENS = {
    # "A1": 5,
    # "E5": 9,
}


def box_id(cell):
    r = ROWS.index(cell[0]) // 3
    c = COLS.index(cell[1]) // 3
    return (r, c)


def make_asterisk_sudoku_csp():
    cells = cross(ROWS, COLS)

    domains = {c: [GIVENS[c]] if c in GIVENS else list(range(1, 10)) for c in cells}

    neighbors = {c: [] for c in cells}
    for x in cells:
        for y in cells:
            if x == y:
                continue
            same_row = x[0] == y[0]
            same_col = x[1] == y[1]
            same_box = box_id(x) == box_id(y)
            same_ast = x in ASTERISK_CELLS and y in ASTERISK_CELLS
            if same_row or same_col or same_box or same_ast:
                neighbors[x].append(y)

    def diff_constraint(X, x, Y, y):
        return x != y

    sudokuCSP = CSP(
        variables=cells,
        domains=domains,
        neighbors=neighbors,
        constraints=diff_constraint,
    )
    return sudokuCSP
