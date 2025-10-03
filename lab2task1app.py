# Import dependencies
import streamlit as st
import streamlit.components.v1 as components  # keep if you show HTML later
from PIL import Image

from src.trivialVacuumEnvironmentClass import TrivialVacuumEnvironment
from src.agents import RandomVacuumAgent, TableDrivenVacuumAgent, ReflexAgent

# ----- canonical env-state images -----
env1 = {(0, 0): 'Clean', (1, 0): 'Clean'}
env2 = {(0, 0): 'Clean', (1, 0): 'Dirty'}
env3 = {(0, 0): 'Dirty', (1, 0): 'Clean'}
env4 = {(0, 0): 'Dirty', (1, 0): 'Dirty'}

def getImg(agentLoc, envState):
    # Choose an image based on agent location and the two-room cleanliness.
    # NOTE: dict equality compares by content, so this works.
    if agentLoc == (0, 0):
        if envState == env1:
            image = Image.open("imgs/a_clean_Agent__b_clean.jpg")
        elif envState == env2:
            image = Image.open("imgs/a_clean_Agent__b_dirty.jpg")
        elif envState == env3:
            image = Image.open("imgs/a_dirty_Agent__b_clean.jpg")
        else:  # env4
            image = Image.open("imgs/a_dirty_Agent__b_dirty.jpg")
    else:  # agentLoc == (1, 0)
        if envState == env1:
            image = Image.open("imgs/a_clean__b_clean_Agent.jpg")
        elif envState == env2:
            image = Image.open("imgs/a_clean__b_dirty_Agent.jpg")
        elif envState == env3:
            image = Image.open("imgs/a_dirty__b_clean_Agent.jpg")
        else:  # env4
            image = Image.open("imgs/a_dirty__b_dirty_Agent.jpg")
    return image

# ----- session state helpers -----
AGENTS = {
    "Random": RandomVacuumAgent,
    "Table-Driven": TableDrivenVacuumAgent,
    "Reflex": ReflexAgent,
}

def init_state(default_agent="Reflex"):
    if "env" not in st.session_state:
        st.session_state.env = TrivialVacuumEnvironment()
    if "agent" not in st.session_state:
        st.session_state.agent = AGENTS[default_agent]()
        st.session_state.env.add_thing(st.session_state.agent)

def reset_env(agent_name):
    st.session_state.env = TrivialVacuumEnvironment()
    st.session_state.agent = AGENTS[agent_name]()
    st.session_state.env.add_thing(st.session_state.agent)

# ----- one-step callback -----
def AgentStep(*args, **kwargs):
    env = st.session_state.env
    agent = st.session_state.agent

    # percept -> action
    percept = env.percept(agent)
    action = agent.program(percept)

    # apply action
    env.execute_action(agent, action)

    # report + redraw
    st.success(f"Agent decided to do: {action}.")
    st.info(f"{type(agent).__name__} is located at {agent.location} now.")
    st.info(f"Current Agent performance: {agent.performance}.")
    st.info(f"State of the Environment: {env.status}.")

    image = getImg(agent.location, env.status)
    st.image(image, caption="Agent is here", use_container_width=True)

# ----- streamlit app -----
def main():
    st.title("Simple Agents - lab2. Example1")
    st.header("_Initial Env._", divider=True)

    # choose agent + reset/new env
    choice = st.selectbox("Pick agent type", list(AGENTS.keys()), index=2)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Reset / New Environment"):
            reset_env(choice)
    # ensure state exists after potential reset
    init_state(default_agent=choice)

    # read current state
    env = st.session_state.env
    agent = st.session_state.agent

    st.info(f"{type(agent).__name__} has the initial performance: {agent.performance}")
    st.info(f"State of the Environment: {env.status}.")
    st.info(f"Agent in location {agent.location}.")

    image = getImg(agent.location, env.status)
    st.image(image, caption="Agent is here", use_container_width=True)

    st.button("Run one agent step", on_click=AgentStep, key="step_btn")

if __name__ == "__main__":
    main()
