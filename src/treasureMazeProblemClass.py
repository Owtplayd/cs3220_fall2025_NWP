# src/treasureMazeProblemClass.py
from src.problemClass import Problem


class TreasureMazeProblem(Problem):
    """
    Graph-search problem over an undirected maze.
    State is the current node id (str).
    Actions are neighboring node ids (moving to that neighbor).
    """

    def __init__(self, initial, goal, graph):
        super().__init__(initial, goal)
        self.graph = graph  # instance of src.graphClass.Graph

    def actions(self, A):
        # neighbors of node A
        return list(self.graph.get(A).keys())

    def result(self, state, action):
        # moving to neighbor labelled by its node id
        return action

    def path_cost(self, cost_so_far, A, action, B):
        # use stored edge weights if present; default 1
        edge_cost = self.graph.get(A, B)
        return cost_so_far + (edge_cost if edge_cost is not None else 1)
