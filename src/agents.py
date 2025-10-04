from src.agentPrograms import *
from src.agentClass import Agent

from src.rules import vacuumRules
from src.rules import actionList
from src.rules import table
from src.rules import crazy_house_actions

"""Randomly choose one of the actions from the vacuum environment"""


def RandomVacuumAgent():
    return Agent(RandomAgentProgram(actionList))


def TableDrivenVacuumAgent():
    return Agent(TableDrivenAgentProgram(table))


def ReflexAgent():
    return Agent(ReflexAgentProgram(vacuumRules, interpret_input, rule_match))


def ReflexAgentA2pro():
    pass
    # your code here


# -------------------- Crazy House Task 1 --------------------
def RandomCrazyHouseCat(start_perf: int = 0, name: str = "Cat"):
    """
    Random agent for the Crazy House.
    Ignores percepts; randomly picks one of:
    ['MoveRight','MoveLeft','Eat','Drink','Fight'].
    You can set a custom starting performance with start_perf if desired.
    """
    a = Agent(program=RandomAgentProgram(crazy_house_actions), name=name)
    a.performance = int(start_perf)
    return a
