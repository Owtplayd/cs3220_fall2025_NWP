# src/trivialVacuumEnvironmentClass.py
from src.environmentClass import Environment
from src.locations import loc_A, loc_B
from src.agentClass import Agent
from src.thingClass import Thing
import random


class TrivialVacuumEnvironment(Environment):
    """
    Two-location vacuum world (A and B).
    State: dict {loc_A: 'Clean'|'Dirty', loc_B: 'Clean'|'Dirty'}
    Percept to agent: (agent.location, status_at_location)
    Actions: 'Left', 'Right', 'Suck', 'NoOp'
    Rewards:
      +10 for cleaning a dirty square with 'Suck'
      -1  for moving (Left/Right) or for useless 'Suck' (already clean)
       0  for 'NoOp'
    """

    def __init__(self):
        super().__init__()
        self.status = {
            loc_A: random.choice(["Clean", "Dirty"]),
            loc_B: random.choice(["Clean", "Dirty"]),
        }

    # --- Agent I/O --------------------------------------------------------
    def percept(self, agent: Agent):
        """Return (agent.location, status_at_location)."""
        return agent.location, self.status[agent.location]

    # --- Life/Housekeeping ------------------------------------------------
    def is_agent_alive(self, agent: Agent):
        return getattr(agent, "alive", True)

    def update_agent_alive(self, agent: Agent):
        agent.alive = True  # Task 1 never terminates the agent

    # --- Action effects ---------------------------------------------------
    def execute_action(self, agent: Agent, action: str):
        if action == "Right":
            if agent.location == loc_A:
                agent.location = loc_B
            agent.performance -= 1
            self.update_agent_alive(agent)

        elif action == "Left":
            if agent.location == loc_B:
                agent.location = loc_A
            agent.performance -= 1
            self.update_agent_alive(agent)

        elif action == "Suck":
            if self.status[agent.location] == "Dirty":
                agent.performance += 10
                self.status[agent.location] = "Clean"
            else:
                agent.performance -= 1
            self.update_agent_alive(agent)

        elif action == "NoOp":
            # zero-cost idle in this baseline
            self.update_agent_alive(agent)

        else:
            raise ValueError(f"Unknown action: {action}")

    # --- Placement --------------------------------------------------------
    def default_location(self, thing: Thing):
        """Agents start in either location at random."""
        print("Agent is starting in random location...")
        return random.choice([loc_A, loc_B])
