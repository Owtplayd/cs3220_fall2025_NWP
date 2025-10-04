# src/environmentProClass.py
from src.environmentClass import Environment
from src.thingClass import Thing
from src.agentClass import Agent
import random
from typing import List, Optional


# ------------------------ Things ------------------------
class Mouse(Thing):
    pass


class Milk(Thing):
    pass


class Dog(Thing):
    pass


# ------------------------ Crazy House Environment ------------------------
class environmentPro(Environment):
    """
    Task 1: Crazy House

    House: N rooms in a line (default 5).
    Things: Mouse, Milk, Dog placed randomly with constraints:

      • If Mouse & Milk placed in same room -> keep Mouse, remove Milk.
      • If Mouse & Dog placed in same room -> move Mouse randomly to previous OR next room.
      • Dog & Milk may share a room.

    Cat (Agent) actions allowed anywhere (random agent):
      MoveRight, MoveLeft, Eat, Drink, Fight

    Rewards:
      Drink: +5 (remove Milk)
      Eat: +10 if performance >= 3 (remove Mouse)
      Move: -1
      Fight Dog:
         win if performance >= 10 => +20
         else => -10

    Game over if performance <= 0.
    """

    crazy_actions = ["MoveRight", "MoveLeft", "Eat", "Drink", "Fight"]

    def __init__(self, n_rooms: int = 5):
        super().__init__()
        self.n_rooms = max(2, n_rooms)
        self.rooms: List[List[Thing]] = [[] for _ in range(self.n_rooms)]
        self.things: List[Thing] = []

    # ---------- helpers ----------
    def default_location(self, thing: Thing) -> int:
        return random.randint(0, self.n_rooms - 1)

    def _room_bounds(self, i: int) -> int:
        return max(0, min(self.n_rooms - 1, i))

    def _enforce_placement_constraints(self, room_idx: int):
        """
        Enforce placement-only constraints after adding a non-agent thing.
        - Mouse + Milk  -> remove Milk (keep Mouse)
        - Mouse + Dog   -> move Mouse randomly to prev or next room (bounded)
        """
        room = self.rooms[room_idx]
        mice = [t for t in room if isinstance(t, Mouse)]
        milks = [t for t in room if isinstance(t, Milk)]
        dogs = [t for t in room if isinstance(t, Dog)]

        # Mouse + Milk -> remove all Milks in that room
        if mice and milks:
            for m in list(milks):
                room.remove(m)
                if m in self.things:
                    self.things.remove(m)

        # Mouse + Dog -> move each Mouse randomly to prev or next (within bounds)
        if mice and dogs:
            for mouse in list(mice):
                room.remove(mouse)
                # choose -1 (prev) or +1 (next); if out-of-bounds, flip direction
                step = random.choice([-1, 1])
                new_idx = room_idx + step
                if not (0 <= new_idx < self.n_rooms):
                    new_idx = room_idx - step
                new_idx = self._room_bounds(new_idx)
                self.rooms[new_idx].append(mouse)
                # single pass on the destination room to handle Mouse+Milk there, etc.
                self._resolve_mouse_milk_only(new_idx)

    def _resolve_mouse_milk_only(self, room_idx: int):
        """Used when we just moved a mouse; ensures Mouse+Milk => no Milk."""
        room = self.rooms[room_idx]
        mice = any(isinstance(t, Mouse) for t in room)
        if not mice:
            return
        for t in list(room):
            if isinstance(t, Milk):
                room.remove(t)
                if t in self.things:
                    self.things.remove(t)

    # ---------- core API ----------
    def add_thing(self, thing: Thing, location: Optional[int] = None):
        """Add Agents or Things. For Things, apply placement constraints."""
        if isinstance(thing, Agent):
            if thing in self.agents:
                return
            thing.location = (
                self.default_location(thing) if location is None else int(location)
            )
            thing.alive = True
            # keep whatever starting performance the Agent already has
            self.agents.append(thing)
            return

        # Non-agent thing (scene)
        if thing in self.things:
            return
        room_idx = self.default_location(thing) if location is None else int(location)
        room_idx = self._room_bounds(room_idx)
        self.rooms[room_idx].append(thing)
        self.things.append(thing)
        self._enforce_placement_constraints(room_idx)

    def percept(self, agent: Agent):
        """Return (room_index, tuple(sorted(things by class name in that room)))."""
        idx = int(agent.location)
        names = sorted(t.__class__.__name__ for t in self.rooms[idx])
        return (idx, tuple(names))

    def is_agent_alive(self, agent: Agent) -> bool:
        return getattr(agent, "alive", True)

    def _update_alive_from_performance(self, agent: Agent):
        # Game over if performance <= 0
        agent.alive = agent.performance > 0

    def execute_action(self, agent: Agent, action: str):
        if not self.is_agent_alive(agent):
            return

        idx = int(agent.location)
        action = str(action)

        # ---- movement ----
        if action == "MoveRight":
            if idx < self.n_rooms - 1:
                agent.location = idx + 1
            agent.performance -= 1
            self._update_alive_from_performance(agent)
            return

        if action == "MoveLeft":
            if idx > 0:
                agent.location = idx - 1
            agent.performance -= 1
            self._update_alive_from_performance(agent)
            return

        here = self.rooms[int(agent.location)]

        # ---- drink ----
        if action == "Drink":
            milk = next((t for t in here if isinstance(t, Milk)), None)
            if milk:
                agent.performance += 5
                here.remove(milk)
                if milk in self.things:
                    self.things.remove(milk)
            self._update_alive_from_performance(agent)
            return

        # ---- eat ----
        if action == "Eat":
            mouse = next((t for t in here if isinstance(t, Mouse)), None)
            if mouse and agent.performance >= 3:
                agent.performance += 10
                here.remove(mouse)
                if mouse in self.things:
                    self.things.remove(mouse)
            # (if weak or no mouse, nothing happens)
            self._update_alive_from_performance(agent)
            return

        # ---- fight ----
        if action == "Fight":
            dog = next((t for t in here if isinstance(t, Dog)), None)
            if dog:
                if agent.performance >= 10:
                    agent.performance += 20  # win (dog stays; spec doesn't say remove)
                else:
                    agent.performance -= 10  # lose
            self._update_alive_from_performance(agent)
            return

        # Unknown action: no-op but still check alive
        self._update_alive_from_performance(agent)
