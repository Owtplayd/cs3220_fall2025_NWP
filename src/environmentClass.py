'''
A base class representing an abstract Environment.
'Real' Environment classes must inherit from this one.
The environment keeps a list of .agents.
Each agent has a .performance slot, initialized to 0.
'''

from src.agentClass import Agent

class Environment:
  def __init__(self):
    # List of agents currently in the environment
    self.agents = []

  # -----------------------------
  # Perception / Action interface
  # -----------------------------
  def percept(self, agent):
    # Return the percept that the agent sees at this point.
    # Implement this in derived classes.
    raise NotImplementedError("Environment.percept must be implemented by a subclass.")

  def execute_action(self, agent, action):
    # Apply the action to the world and update performance, etc.
    # Implement this in derived classes.
    raise NotImplementedError("Environment.execute_action must be implemented by a subclass.")

  # -----------------------------
  # Placement helpers
  # -----------------------------
  def default_location(self, thing):
    # Fallback start location. Concrete envs usually override this.
    return (0, 0)

  def add_thing(self, thing, location=None):
    # Add an Agent (or Thing) into the environment at a given location.
    # For Task 1 we only use Agents; Things come in Task 2.
    if thing in self.agents:
      print("Can't add the same agent twice")
      return
    if isinstance(thing, Agent):
      thing.performance = 0
      thing.alive = True
      thing.location = location if location is not None else self.default_location(thing)
      self.agents.append(thing)

  def delete_thing(self, thing):
    # Remove an Agent from the environment (Things in Task 2+)
    if thing in self.agents:
      self.agents.remove(thing)

  # -----------------------------
  # Simulation loop
  # -----------------------------
  def is_done(self):
    # End when no agent is alive
    return not any(getattr(a, "alive", True) for a in self.agents)

  def step(self):
    # One turn for every agent currently in the world
    for agent in list(self.agents):
      if not getattr(agent, "alive", True):
        continue
      percept = self.percept(agent)          # (location, status)
      action = agent.program(percept)        # agent decides
      self.execute_action(agent, action)     # env applies + updates performance/alive

  def run(self, steps=10):
    # Run for at most 'steps' iterations or until is_done()
    for _ in range(steps):
      if self.is_done():
        break
      self.step()
