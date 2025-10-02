import random

'''An idea of Random Agent Program is to choose an action at random, ignoring all percepts'''
def RandomAgentProgram(actions):
   return lambda percept: random.choice(actions)

def TableDrivenAgentProgram(table):
    """
    This agent selects an action based on the percept sequence.
    To customize it, provide as table a dictionary of all 
    {percept_sequence:action} pairs.
    IMPORTANT: keys are tuples of percepts, so we cast the running list
    to a tuple before lookup.
    """
    percepts = []

    def program(percept):
        percepts.append(percept)
        # tuple-of-percepts is required by the table dictionary keys
        return table[tuple(percepts)]
    return program

# -----------------------------------
# Reflex agent program for Task 1
# -----------------------------------
def ReflexAgentProgram(rules, interpret_input, rule_match):
  """
  Classic reflex agent: interpret percept -> abstract state,
  then match a rule for that state to get an action.
  """
  def program(percept):
    state = interpret_input(percept)
    return rule_match(state, rules)
  return program

def interpret_input(percept):
  """
  For Task 1, the percept is already (location_tuple, 'Clean'|'Dirty').
  We just forward it as the state.
  """
  return percept

def rule_match(state, rules):
  """
  For Task 1, rules are keyed directly by the state tuple.
  Example key: ((0,0), 'Dirty') -> 'Suck'
  """
  return rules[state]

# -----------------------------------------------------
# (A2/company) Below are stubs used later in Task 3.
# Keep them as-is for now so imports don’t break.
# -----------------------------------------------------
# Interpreter for the "pro" (company) environment is defined
# in the instructor notebook. We keep placeholders compatible
# with rules.py:a2proRules usage.
def interpret_input_A2pro(percepts):
  """
  The instructor demonstrates interpreting a list of percepts
  into a label like 'Office manager', 'IT', 'Student', 'Clear', 'Last room'.
  Keep the exact behavior for Task 3. We provide a minimal version
  that mirrors the style from class; you will expand it in Task 3.
  """
  status = 'Clear'
  try:
    from src.Task3YourClasses import OfficeManager, ITStuff, Student
  except Exception:
    # If classes aren’t defined yet, we just return the default
    pass

  # If the last percept is the sentinel (e.g., None) we treat as last room
  if percepts and percepts[-1] == 'Last room':
    status = 'Last room'
  else:
    for p in percepts:
      # We only do isinstance checks if classes exist.
      try:
        from src.Task3YourClasses import OfficeManager, ITStuff, Student
        if isinstance(p, OfficeManager):
          return 'Office manager'
        elif isinstance(p, ITStuff):
          return 'IT'
        elif isinstance(p, Student):
          return 'Student'
      except Exception:
        # Without Task3 classes loaded, fall back to 'Clear'
        status = 'Clear'
  return status

def rule_match_A2pro(state, rules):
  return rules[state]
