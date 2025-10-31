# ==========================================================
# run_task2_asterisk.py
# Runner for Lab 6 – Task 2
# ==========================================================

from data_lab6_task2_asteriskSudokuCSP import make_asterisk_sudoku_csp
from csp_AC3_agentProgram import run_AC3_on_csp

if __name__ == "__main__":
    csp = make_asterisk_sudoku_csp()
    run_AC3_on_csp(csp, make_html=True, html_prefix="asterisk")
    # PDF: "output the resulting domain for all cells" – already done
    # by run_AC3_on_csp
