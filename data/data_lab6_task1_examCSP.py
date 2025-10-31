# ==========================================================
# data_lab6_task1_examCSP.py
# Data file for Lab 6 – Task 1 (Exam Schedule CSP)
# ==========================================================

from src.CSPclass import CSPBasic
from src.utils import different_values_constraint

def make_exam_csp():
    courses = [
        "Algorithms I",
        "Introduction to File and Database Management",
        "Practical Programming Methodology",
        "Computer Organization and Architecture I",
        "Linear Algebra I",
        "Introduction to Applied Statistics I",
        "Operating Systems",
    ]

    domains = {
        "Algorithms I": ["Mon", "Tue", "Wed"],
        "Introduction to File and Database Management": ["Tue"],
        "Practical Programming Methodology": ["Mon", "Tue", "Wed"],
        "Computer Organization and Architecture I": ["Mon", "Tue", "Wed"],
        "Linear Algebra I": ["Mon", "Tue", "Wed"],
        "Introduction to Applied Statistics I": ["Wed"],
        "Operating Systems": ["Mon", "Tue", "Wed"],
    }

    # main restriction -> all different (complete graph)
    neighbors = {c: [x for x in courses if x != c] for c in courses}

    examCSP = CSPBasic(
        variables=courses,
        domains=domains,
        neighbors=neighbors,
        constraints=different_values_constraint
    )
    return examCSP
