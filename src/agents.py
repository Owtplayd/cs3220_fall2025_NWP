# from src.agentPrograms import *
# from src.agentClass import Agent

# from src.rules import vacuumRules
# from src.rules import actionList
# from src.rules import table




# '''Randomly choose one of the actions from the vacuum environment'''
# def RandomVacuumAgent():
#     return Agent(RandomAgentProgram(actionList))


# def TableDrivenVacuumAgent():
#      return Agent(TableDrivenAgentProgram(table))
 
 
# def ReflexAgent() :
#   return Agent(ReflexAgentProgram(vacuumRules,interpret_input,rule_match))


# def ReflexAgentA2pro():
#     pass
#     #your code here
  

# for the Assignment3

from src.PS_agentPrograms import *
from src.vacuumProblemSolvingAgentSMARTClass import VacuumProblemSolvingAgentSMART
#from vacuumProblemSolvingAgentShowClass import VacuumProblemSolvingAgentDraw
from src.navProblemSolvingAgentClass import navProblemSolvingAgent

def ProblemSolvingVacuumAgentBFS(initState,vacuumWorldGraph,goalState):
    return VacuumProblemSolvingAgentSMART(initState,vacuumWorldGraph,goalState,BestFirstSearchAgentProgram())

 
def ProblemSolvingNavAgentBFS(initState,WorldGraph,goalState):
    return navProblemSolvingAgent(initState,WorldGraph,goalState,BestFirstSearchAgentProgram())

# def ProblemSolvingVacuumAgentBFSwithShow(initState,vacuumWorldGraph,goalState):
#     return VacuumProblemSolvingAgentDraw(initState,vacuumWorldGraph,goalState,BestFirstSearchAgentProgramForShow())