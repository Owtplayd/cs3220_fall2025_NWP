from src.environmentClass import Environment
from src.locations import *

import random

class TrivialVacuumEnvironment(Environment):
  '''
  Two-location vacuum world (A,B). Locations are either 'Clean' or 'Dirty'.
  Percept = (agent.location, status_at_location).
  Actions: 'Left', 'Right', 'Suck', 'NoOp'
  Performance: move = -1; Suck on Dirty = +10; Suck on Clean = -1.
  '''

  def __init__(self):
    super().__init__()
    self.status = {
      loc_A: random.choice(['Clean', 'Dirty']),
      loc_B: random.choice(['Clean', 'Dirty'])
    }

  # --------------
  # Perception
  # --------------
  def percept(self, agent):
    # Returns the agent's location, and the location status (Dirty/Clean).
    return agent.location, self.status[agent.location]

  # --------------
  # Life / Alive
  # --------------
  def is_agent_alive(self, agent):
    return getattr(agent, "alive", True)

  def update_agent_alive(self, agent):
    # In our labs we consider the agent "dead" (stop acting) if performance <= 0
    if agent.performance <= 0:
      agent.alive = False

  # --------------
  # Actions
  # --------------
  def execute_action(self, agent, action):
    if action == 'Right':
      agent.location = loc_B
      agent.performance -= 1
      self.update_agent_alive(agent)

    elif action == 'Left':
      agent.location = loc_A
      agent.performance -= 1
      self.update_agent_alive(agent)

    elif action == 'Suck':
      if self.status[agent.location] == 'Dirty':
        # correct action on Dirty
        self.status[agent.location] = 'Clean'
        agent.performance += 10
      else:
        # wrong action on Clean => small penalty (matches prof’s demo style)
        agent.performance -= 1
      self.update_agent_alive(agent)

    elif action == 'NoOp':
      # No operation: do nothing, no reward/penalty
      pass

    else:
      # Unknown action: ignore
      pass

  # --------------
  # Start placement
  # --------------
  def default_location(self, thing):
    """Agents start in either location at random."""
    return random.choice([loc_A, loc_B])
