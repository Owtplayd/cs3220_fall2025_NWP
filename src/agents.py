from src.agentPrograms import *
from src.agentClass import Agent

from src.rules import vacuumRules
from src.rules import actionList
from src.rules import table
from src.rules import crazy_house_actions

from src.rules_cat import feedingRules, cat_actions
from src.foodClass import Food, Milk, Sausage

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


# -------------------- Task 2: Cat-Friendly-House --------------------
class AgentCat(Agent):
    """
    Cat that can eat Sausage and drink Milk.
    Performance adjustments depend on food calories and weight.
    Movement cost is handled by the Environment.
    """

    def __init__(self, program=None, name="Agent-Cat"):
        super().__init__(program=program, name=name)

    # You can tweak these methods to match your instructor's constants exactly.
    # Default rule: delta = calories - weight
    def eat(self, food: Food):
        if isinstance(food, Sausage):
            self.performance += food.calories - food.weight

    def drink(self, food: Food):
        if isinstance(food, Milk):
            self.performance += food.calories - food.weight


def TableDrivenCatAgent(name: str = "Agent-Cat") -> AgentCat:
    """
    Returns an Agent-Cat that follows the table-driven program using feedingRules.
    """
    prog = TableDrivenAgentProgram(feedingRules)
    return AgentCat(program=prog, name=name)
