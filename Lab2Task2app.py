# lab2task2app.py  — Lab 2 Task 2: Cat, Mouse & Milk
# Place at project root (same level as lab2task1app.py)

import os, sys, random
import streamlit as st

# --- Make 'src/' importable by bare imports like 'agentClass'
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(PROJECT_ROOT, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

# --- IMPORTANT: use the SAME Agent import path as environmentProClass.add_thing()
#     It uses 'from agentClass import Agent', so we do exactly that here.
from agentClass import Agent as BaseAgent

# The rest can safely use 'src.' imports.
from src.CatMouseEnvironmentClass import CatMouseEnvironment
from src.Task2YourClasses import Cat, Milk

# ---------- simple reflex-ish "Mouse" program ----------
def MouseReflexProgram():
    """
    Percept is (location, [things_here]).
    Policy:
      - If Cat here -> 'Run'
      - Else if Milk here -> 'Drink'
      - Else wander: 'Left' or 'Right' (random)
    """
    def program(percept):
        location, things_here = percept
        has_cat  = any(t.__class__.__name__ == "Cat"  for t in things_here)
        has_milk = any(t.__class__.__name__ == "Milk" for t in things_here)
        if has_cat:
            return 'Run'
        if has_milk:
            return 'Drink'
        return random.choice(['Left', 'Right'])
    return program

def MouseAgent():
    return BaseAgent(MouseReflexProgram())

# ---------- session helpers ----------
def reset_env(seed=None):
    if seed is not None:
        random.seed(seed)
    env = CatMouseEnvironment()
    # Add the agent first, then one Cat and one Milk (random placement via env.default_location)
    env.add_thing(MouseAgent())
    env.add_thing(Cat())
    env.add_thing(Milk())
    return env

def get_state_snapshot(env, agent):
    here = [t.__class__.__name__ for t in env.things if getattr(t, "location", None) == agent.location]
    there = [t.__class__.__name__ for t in env.things if getattr(t, "location", None) != agent.location]
    return {
        "agent_location": agent.location,
        "things_here": here,
        "things_elsewhere": there,
        "performance": agent.performance,
        "alive": getattr(agent, "alive", True)
    }

# ---------- callbacks ----------
def do_step():
    env = st.session_state.env
    agent = st.session_state.agent
    if not getattr(agent, "alive", True):
        st.warning("Agent is not alive. Reset to start again.")
        return
    percept = env.percept(agent)
    action = agent.program(percept)
    env.execute_action(agent, action)
    st.session_state.last_action = action

# ---------- UI ----------
def main():
    st.title("Lab 2 — Task 2: Cat, Mouse & Milk")
    st.caption("Two-room world with Things. Aligns with Task 1 patterns (performance/alive, random placement).")

    # init
    if "env" not in st.session_state:
        st.session_state.env = reset_env()
        # env.agents will now contain our agent because isinstance matches
        st.session_state.agent = st.session_state.env.agents[0]
        st.session_state.last_action = None

    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        if st.button("Reset (random)"):
            st.session_state.env = reset_env()
            st.session_state.agent = st.session_state.env.agents[0]
            st.session_state.last_action = None
    with col2:
        seed = st.number_input("Seed", min_value=0, value=0, step=1, help="Use a seed for repeatable layouts.")
        if st.button("Reset with Seed"):
            st.session_state.env = reset_env(seed=seed)
            st.session_state.agent = st.session_state.env.agents[0]
            st.session_state.last_action = None
    with col3:
        st.button("Run one step", on_click=do_step)

    env = st.session_state.env
    agent = st.session_state.agent
    snap = get_state_snapshot(env, agent)

    st.subheader("Current State")
    st.write(f"Agent location: **{snap['agent_location']}**")
    st.write(f"Things here: **{snap['things_here']}**")
    st.write(f"Things elsewhere: **{snap['things_elsewhere']}**")
    st.write(f"Performance: **{snap['performance']}**  |  Alive: **{snap['alive']}**")
    if st.session_state.last_action:
        st.info(f"Last action: **{st.session_state.last_action}**")

    if env.is_done():
        st.success("Episode finished (no milk left or agent died). Reset to run again.")

if __name__ == "__main__":
    main()
