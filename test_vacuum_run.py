from src.trivialVacuumEnvironmentClass import TrivialVacuumEnvironment
from src.agents import RandomVacuumAgent, TableDrivenVacuumAgent, ReflexAgent

def run_once(factory, steps=10):
    env = TrivialVacuumEnvironment()
    agent = factory()
    env.add_thing(agent)
    print("Initial:", env.status)
    env.run(steps=steps)
    print("Final:  ", env.status, "Perf:", agent.performance)

print("=== Random Agent ===")
run_once(RandomVacuumAgent)

print("\n=== Table Agent ===")
run_once(TableDrivenVacuumAgent)

print("\n=== Reflex Agent ===")
run_once(ReflexAgent)
