# src/treasureMazeAgentClass.py
import collections
from src.problemSolvingAgentProgramClass import SimpleProblemSolvingAgentProgram
from src.PS_agentPrograms import BestFirstSearchAgentProgram
from src.treasureMazeProblemClass import TreasureMazeProblem


class TreasureMazeAgent(SimpleProblemSolvingAgentProgram):
    """
    Problem-solving agent for the Treasure Maze.
    Uses your Best-First-Search program (same interface as in Romania example).
    Planning happens in graph neighbor steps; the environment exposes 'advance'
    to consume one planned move per click/step.
    """

    def __init__(
        self,
        initial_state=None,
        dataGraph=None,
        exit_node=None,
        treasures=None,
        program=None,
    ):
        super().__init__(initial_state)
        self.dataGraph = dataGraph
        self.exit_node = exit_node
        self.treasures = treasures or {}  # node -> emoji
        self.have_treasure = False
        self.treasure_picked = None

        # Initial performance = floor(50% of number of nodes)
        n_nodes = len(self.dataGraph.nodes()) if self.dataGraph else 0
        self.performance = max(0, int(0.5 * n_nodes))

        # Planner function (returns a Node pointing to goal)
        if program is None or not isinstance(program, collections.abc.Callable):
            program = BestFirstSearchAgentProgram()
        self.program = program

    # ----- hooks required by SimpleProblemSolvingAgentProgram -----

    def update_state(self, state, percept):
        # Here, percept is already the node-id the agent is at.
        return percept

    def formulate_goal(self, state):
        """
        If we don't have a treasure yet, choose the NEAREST treasure (by planned
        path length). Once we have one, head for the exit.
        """
        if self.have_treasure:
            return self.exit_node

        treasure_nodes = list(self.treasures.keys())
        if not treasure_nodes:
            return self.exit_node

        best_goal = None
        best_len = None
        for t in treasure_nodes:
            problem = TreasureMazeProblem(state, t, self.dataGraph)
            goal_node = self.program(problem)
            if goal_node is None:
                continue
            steps_len = len(goal_node.path()) - 1
            if best_len is None or steps_len < best_len:
                best_len = steps_len
                best_goal = t

        return best_goal if best_goal is not None else self.exit_node

    def formulate_problem(self, state, goal):
        return TreasureMazeProblem(state, goal, self.dataGraph)

    def search(self, problem):
        """
        Run best-first search and return a list of actions (neighbor node-ids)
        forming the plan. The base class stores this list into self.seq.
        """
        goal_node = self.program(problem)
        if goal_node is None:
            return []
        return goal_node.solution()  # list of actions (target node-ids)

    # Convenience for the environment/UI to refresh a plan on demand.
    def replan(self):
        # Trigger the base pipeline: update -> formulate_goal -> formulate_problem -> search
        # Base __call__ expects a percept; we pass current state.
        self(self.state)
        return list(self.seq)
