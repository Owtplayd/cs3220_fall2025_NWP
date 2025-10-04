# src/catFriendlyHouseEnvironmentClass.py
import random
from typing import Dict, Optional

from src.environmentClass import Environment
from src.agentClass import Agent
from src.locations import loc_A, loc_B
from src.foodClass import Food, Milk, Sausage


class CatFriendlyHouse(Environment):
    """
    A 2-room world in a row (loc_A, loc_B).

    Exactly one Milk and one Sausage are placed, in different rooms.
    The .percept(agent) returns: (agent.location, 'MilkHere' | 'SausageHere' | 'Empty').

    Actions: 'MoveRight', 'MoveLeft', 'Drink', 'Eat'
    Movement costs -1 performance each time.
    Eating/Drinking delegates to the Cat's methods (performance change is handled by the agent).
    """

    def __init__(self):
        super().__init__()
        # rooms -> Optional[Food]
        self.rooms: Dict[tuple, Optional[Food]] = {loc_A: None, loc_B: None}
        self._place_food()

    # -------------------- setup --------------------
    def _place_food(self):
        spots = [loc_A, loc_B]
        milk_loc = random.choice(spots)
        sausage_loc = loc_B if milk_loc == loc_A else loc_A
        # randomize weights but keep calories fixed by class
        self.rooms[milk_loc] = Milk(weight=random.randint(1, 5))
        self.rooms[sausage_loc] = Sausage(weight=random.randint(2, 7))

    def default_location(self, thing):
        # Agents start randomly in A or B
        return random.choice([loc_A, loc_B])

    # -------------------- percept --------------------
    def _room_status(self, location: tuple) -> str:
        item = self.rooms.get(location)
        if isinstance(item, Milk):
            return "MilkHere"
        if isinstance(item, Sausage):
            return "SausageHere"
        return "Empty"

    def percept(self, agent: Agent):
        """
        Return (agent.location, room_status).
        This mirrors the style used in TrivialVacuumEnvironment: (loc, 'Status').
        """
        return (agent.location, self._room_status(agent.location))

    # -------------------- acting --------------------
    def execute_action(self, agent: Agent, action: str):
        if not agent.alive:
            return

        loc = agent.location
        here = self.rooms[loc]

        if action == "MoveRight":
            # A -> B (B -> B)
            agent.performance -= 1
            agent.location = loc_B
            return

        if action == "MoveLeft":
            # B -> A (A -> A)
            agent.performance -= 1
            agent.location = loc_A
            return

        if action == "Drink":
            # Only Milk is drinkable
            if isinstance(here, Milk):
                # Delegate to cat's drink (if method exists), else simple default
                if hasattr(agent, "drink") and callable(agent.drink):
                    agent.drink(here)
                else:
                    # fallback: calories - weight
                    agent.performance += here.calories - here.weight
                # remove from room
                self.rooms[loc] = None
            # if wrong type or empty -> no change
            return

        if action == "Eat":
            # Sausage is edible
            if isinstance(here, Sausage):
                if hasattr(agent, "eat") and callable(agent.eat):
                    agent.eat(here)
                else:
                    agent.performance += here.calories - here.weight
                self.rooms[loc] = None
            return

        # NoOp or unknown: do nothing

    # -------------------- bookkeeping --------------------
    def done(self) -> bool:
        """Finish when both items are gone (both rooms Empty)."""
        return all(self.rooms[r] is None for r in (loc_A, loc_B))

    # convenience for logging/debug
    def show_world(self):
        def show(loc):
            item = self.rooms[loc]
            if item is None:
                return "Empty"
            return f"{item.__class__.__name__}(w={item.weight}, cal={item.calories})"

        return {"A": show(loc_A), "B": show(loc_B)}
