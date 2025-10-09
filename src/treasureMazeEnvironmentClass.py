# src/treasureMazeEnvironmentClass.py
import random
from src.environmentClass import Environment

TREASURE_ICON = {
    "gold": "💰",
    "diamond": "🔷",
    "pizza": "🍕",
    "bonus": "🎉",
}


class TreasureMazeEnvironment(Environment):
    """
    The maze is a Graph (undirected). Treasures are placed on random distinct
    nodes (not at start or exit).
    One environment step consumes one planned move ('advance') from agent.seq.
    """

    def __init__(self, mazeGraph, start_node, exit_node, seed=None):
        super().__init__()
        self.status = mazeGraph  # src.graphClass.Graph
        self.start_node = start_node
        self.exit_node = exit_node
        self.random = random.Random(seed)
        self.treasures = {}  # node -> icon
        self.place_treasures()

    # --- environment API ---
    def percept(self, agent):
        return agent.state

    def is_agent_alive(self, agent):
        return agent.alive

    def add_thing(self, agent):
        super().add_thing(agent)
        agent.state = self.start_node  # drop at entrance

    def place_treasures(self):
        types = list(TREASURE_ICON.keys())
        nodes = [
            n for n in self.status.nodes() if n not in (self.start_node, self.exit_node)
        ]
        self.random.shuffle(nodes)
        chosen = nodes[: min(4, len(nodes))]
        for i, n in enumerate(chosen):
            self.treasures[n] = TREASURE_ICON[types[i % len(types)]]

    # -- core transition for one click/step --
    def _advance_one(self, agent):
        if not agent.seq:
            agent.replan()
        if not agent.seq:
            agent.alive = False
            return

        next_node = agent.seq.pop(0)
        agent.state = next_node
        agent.performance -= 1  # one executed action costs -1

        # pick treasure if present
        if (not agent.have_treasure) and (next_node in self.treasures):
            agent.have_treasure = True
            agent.treasure_picked = self.treasures.pop(next_node)
            # Immediately replan toward the exit on the next call
            agent.seq = []

        # stop when at exit with a treasure
        if agent.have_treasure and agent.state == self.exit_node:
            agent.alive = False

    def execute_action(self, agent, action):
        # Only 'advance' is needed for the planning agent; 'left'/'right' are no-ops with a small cost.
        if action == "advance":
            self._advance_one(agent)
        elif action in ("left", "right"):
            agent.performance -= 1

    def step(self):
        if self.is_done():
            return
        for agent in list(self.agents):
            if not agent.alive:
                continue
            self.execute_action(agent, "advance")

    def is_done(self):
        if not self.agents:
            return True
        return all(not a.alive for a in self.agents)
