# src/agentClass.py
# This subclass of a base Thing class represents an Agent.
# It has one required slot .program (a function: percept -> action),
# and an optional .performance numeric measure.

from src.thingClass import Thing


class Agent(Thing):
    """
    Minimal Agent consistent with your course baseline:
      - program: callable(percept) -> action
      - performance: numeric score (default 0)
      - location: set by Environment.add_thing / default_location
      - alive: bool (default True)
    """

    def __init__(self, program=None, name=None):
        super().__init__()
        self.name = name or "Agent"
        self.program = program if callable(program) else (lambda percept: "NoOp")
        self.performance = 0
        self.location = None
        self.alive = True

    def __call__(self, percept):
        """Run the agent program: percept -> action."""
        return self.program(percept)

    def show_state(self):
        print(f"{self.name}@{self.location} perf={self.performance} alive={self.alive}")
