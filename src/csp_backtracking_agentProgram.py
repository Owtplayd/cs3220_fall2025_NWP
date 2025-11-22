# ==========================================================
# src/csp_backtracking_agentProgram.py
# Generic CSP agent programs for Lab 7:
#   - run_AC3_on_csp: run constraint propagation once (AC-3)
#   - backtracking_with_trace: backtracking search + step trace
# ==========================================================

from src.algorithms import (
    AC3,
    first_unassigned_variable,
)


def run_AC3_on_csp(csp):
    """
    Run AC-3 once on the given CSP.

    Returns (consistent, checks, csp).

    * consistent: True/False – whether any domain became empty
    * checks: number of consistency checks performed
    * csp: the same CSP object, whose curr_domains now hold pruned domains
    """
    consistent, checks = AC3(csp)
    return consistent, checks, csp


def _values_for(csp, var):
    """
    Helper: return the current domain of a variable var.
    Uses curr_domains if available (after AC-3), otherwise the original domains.
    """
    if getattr(csp, "curr_domains", None) is not None:
        return csp.curr_domains[var]
    else:
        return csp.domains[var]


def backtracking_with_trace(csp):
    """
    Backtracking search that records every assignment/unassignment.

    Returns (solution_assignment, steps), where:

      - solution_assignment: dict {var: value} or None
      - steps: list of dicts with keys:
          "step"      : step number (int)
          "event"     : "assign" | "unassign" | "complete"
          "var"       : variable name or None
          "val"       : value or None
          "assignment": snapshot of current partial assignment
    """
    steps = []
    counter = {"n": 0}

    def record(event, var=None, val=None, assignment=None):
        counter["n"] += 1
        steps.append(
            {
                "step": counter["n"],
                "event": event,
                "var": var,
                "val": val,
                "assignment": dict(assignment) if assignment is not None else {},
            }
        )

    def backtrack(assignment):
        # goal test: all variables assigned
        if len(assignment) == len(csp.variables):
            record("complete", assignment=assignment)
            return dict(assignment)

        var = first_unassigned_variable(assignment, csp)

        for value in _values_for(csp, var):
            if csp.nconflicts(var, value, assignment) == 0:
                csp.assign(var, value, assignment)
                record("assign", var, value, assignment)

                result = backtrack(assignment)
                if result is not None:
                    return result

            csp.unassign(var, assignment)
            record("unassign", var, value, assignment)

        return None

    solution = backtrack({})
    return solution, steps
