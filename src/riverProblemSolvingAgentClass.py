# src/riverProblemSolvingAgentClass.py
import collections
from src.problemSolvingAgentProgramClass import SimpleProblemSolvingAgentProgram
from src.riverProblemClass import RiverProblem


class RiverProblemSolvingAgent(SimpleProblemSolvingAgentProgram):
    """
    Problem-solving agent for the Wolf–Goat–Cabbage puzzle.
    Plug in BestFirstSearchAgentProgram() from src.PS_agentPrograms.
    """

    def __init__(self, initial_state=None, goal=None, cost_version="1.0", program=None):
        super().__init__(initial_state)
        self.goal = goal
        self.cost_version = cost_version
        if program is None or not isinstance(program, collections.abc.Callable):
            raise ValueError(
                "Provide a callable search 'program' (e.g., BestFirstSearchAgentProgram())."
            )
        self.program = program

    def update_state(self, state, percept):
        return percept

    def formulate_goal(self, state):
        return self.goal

    def formulate_problem(self, state, goal):
        return RiverProblem(initial=state, goal=goal, cost_version=self.cost_version)

    def search(self, problem):
        actions, steps, _ = self.program(problem)  # returns (plan, steps, colors)
        return actions

    def run(self):
        if self.goal is None:
            raise ValueError("Goal is None.")
        self.state = self.update_state(self.state, self.state)
        problem = self.formulate_problem(self.state, self.goal)
        return self.search(problem)
