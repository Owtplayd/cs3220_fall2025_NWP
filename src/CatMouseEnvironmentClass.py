# src/CatMouseEnvironmentClass.py
import random
from src.environmentProClass import environmentPro
from src.locations import loc_A, loc_B
from src.Task2YourClasses import Cat, Milk


class CatMouseEnvironment(environmentPro):
    """
    Two-location 'house' like the trivial vacuum world, but with Things:
    - Cat  (hazard)
    - Milk (goal)
    Percept  -> (agent.location, [things_at_location])
    Actions  -> 'Left', 'Right', 'Drink', 'Run', 'NoOp'
    Scoring  -> move: -1; Drink on Milk: +5; meet Cat w/o Run: -10 (and die)
    """

    def __init__(self):
        super().__init__()
        self.locations = [loc_A, loc_B]

    # ---------- perception ----------
    def percept(self, agent):
        # Return current location and the list of Things at that location
        here = [t for t in self.things if t.location == agent.location]
        return agent.location, here

    # ---------- placement ----------
    def default_location(self, thing):
        # Start anywhere (random), exactly like your prof showed
        return random.choice(self.locations)

    # ---------- helpers (alive like Task 1) ----------
    def is_agent_alive(self, agent):
        return getattr(agent, "alive", True)

    def update_agent_alive(self, agent):
        # mirror TrivialVacuumEnvironmentClass: stop if performance <= 0
        if agent.performance <= 0:
            agent.alive = False

    # ---------- actions ----------
    def execute_action(self, agent, action):
        if not self.is_agent_alive(agent):
            return

        if action == "Right":
            agent.location = loc_B
            agent.performance -= 1
            self.update_agent_alive(agent)

        elif action == "Left":
            agent.location = loc_A
            agent.performance -= 1
            self.update_agent_alive(agent)

        elif action == "Drink":
            # reward only if Milk is here
            milks = [
                t
                for t in self.things
                if isinstance(t, Milk) and t.location == agent.location
            ]
            if milks:
                agent.performance += 10
                # remove the milk (consumed)
                self.delete_thing(milks[0])
            self.update_agent_alive(agent)

        elif action == "Run":
            # running itself doesn't move you in this simple design,
            # but it's the 'defensive' choice: no penalty or reward.
            # (Movement cost is already handled by Left/Right.)
            pass

        elif action == "NoOp":
            pass

        # After *any* action, check deadly cat situation unless agent chose 'Run'
        # (Instructor note said not to overcomplicate—so we keep it simple:
        # if you share a tile with a Cat and you didn't 'Run' this turn -> big hit.)
        loc, things_here = self.percept(agent)
        if any(isinstance(t, Cat) for t in things_here) and action != "Run":
            agent.performance -= 10
            self.update_agent_alive(agent)

    # ---------- termination ----------
    def is_done(self):
        # Stop if agent died or there is no more milk to drink.
        no_agents_alive = not any(getattr(a, "alive", True) for a in self.agents)
        milk_gone = not any(isinstance(t, Milk) for t in self.things)
        return no_agents_alive or milk_gone
