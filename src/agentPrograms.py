# src/agentPrograms.py
import random

# ---------------------------------------------------------------------
# Random / Table-Driven / Reflex (vacuum example + general pattern)
# ---------------------------------------------------------------------


def RandomAgentProgram(actions):
    """Ignore percepts; pick any action uniformly at random."""
    if not actions:
        raise ValueError("actions must be a non-empty list")
    return lambda percept: random.choice(actions)


def TableDrivenAgentProgram(table):
    """
    Table-driven agent program. 'table' is a dict keyed by tuple(percepts_so_far).
    We keep an internal list of percepts and cast it to a tuple for lookup.
    Percepts are the environment outputs, e.g. (loc, status).
    """
    percepts = []

    def program(percept):
        percepts.append(percept)
        key = tuple(percepts)  # e.g., ((loc_A,'Clean'), (loc_B,'Dirty'))
        if key in table:
            return table[key]
        # Common teaching fallback: try last percept only if full history not in table
        last_key = (percepts[-1],)
        if last_key in table:
            return table[last_key]
        raise KeyError(f"Percept sequence {key} not found in the table.")

    return program


def ReflexAgentProgram(rules, interpret_input, rule_match):
    """
    Generic reflex agent:
      abstract_state = interpret_input(percept)
      action = rule_match(abstract_state, rules)
    'rules' is typically a dict mapping abstract_state -> action.
    """

    def program(percept):
        state = interpret_input(percept)
        return rule_match(state, rules)

    return program


# --- Helpers for your Task 1 vacuum world --------------------------------


def interpret_input(percept):
    """
    Your environment percept is (location, status), where:
      location: loc_A or loc_B (likely (0,0) or (1,0))
      status:   'Dirty' or 'Clean'
    Your rules use keys like  ((0, 0), 'Dirty'), so just pass it through.
    """
    # e.g., percept == ( (0,0), 'Dirty' )
    return percept


def rule_match(state, rules):
    """Strict dictionary lookup to align with your vacuumRules."""
    return rules[state]


# --- (kept for later tasks; not used in Task 1) ---------------------------


def interpret_input_A2pro(percept):
    return percept


def rule_match_A2pro(state, rules):
    return rules[state]
