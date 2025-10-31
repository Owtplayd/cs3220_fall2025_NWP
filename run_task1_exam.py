# ==========================================================
# run_task1_exam.py
# Runner for Lab 6 – Task 1
# ==========================================================

from data_lab6_task1_examCSP import make_exam_csp
from csp_AC3_agentProgram import run_AC3_on_csp

if __name__ == "__main__":
    csp = make_exam_csp()
    run_AC3_on_csp(csp, make_html=True, html_prefix="exams")

    # PDF wants these 3 specifically:
    print("\nRequested 3 variables:")
    for v in [
        "Practical Programming Methodology",
        "Computer Organization and Architecture I",
        "Linear Algebra I",
    ]:
        print(f"{v}: {csp.curr_domains[v]}")
