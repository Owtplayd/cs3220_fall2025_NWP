# Import dependencies
import streamlit as st
import streamlit.components.v1 as components #to display the HTML code

from PIL import Image

import random

from src.trivialVacuumEnvironmentClass import TrivialVacuumEnvironment
from src.agents import RandomVacuumAgent

env1={(0, 0): 'Clean', (1, 0): 'Clean'}
env2={(0, 0): 'Clean', (1, 0): 'Dirty'}
env3={(0, 0): 'Dirty', (1, 0): 'Clean'}
env4={(0, 0): 'Dirty', (1, 0): 'Dirty'}



def getImg (agentLoc, envState):
    if agentLoc==(0,0):
        if envState==env1:
            # Load an image
            image = Image.open("imgs/a_clean_Agent__b_clean.jpg") # Replace with your image path
        elif envState==env2:
            image = Image.open("imgs/a_clean_Agent__b_dirty.jpg")
        elif envState==env3:
            image = Image.open("imgs/a_dirty_Agent__b_clean.jpg")
        elif envState==env4:
            image = Image.open("imgs/a_dirty_Agent__b_dirty.jpg")            

    elif agentLoc==(1,0):
        if envState==env1:
            # Load an image
            image = Image.open("imgs/a_clean__b_clean_Agent.jpg") # Replace with your image path
        elif envState==env2:
            image = Image.open("imgs/a_clean__b_dirty_Agent.jpg")
        elif envState==env3:
            image = Image.open("imgs/a_dirty__b_clean_Agent.jpg")
        elif envState==env4:
            image = Image.open("imgs/a_dirty__b_dirty_Agent.jpg")
    
    return image

def drawBtn(e,a):
    option= [e,a]
    st.button("Run One Agent's Step", on_click= AgentStep, args= [option])
    
def AgentStep(opt):
    st.session_state["clicked"] = True
    e,a= opt[0],opt[1]
    
    if e.is_agent_alive(a):
        stepActs=e.step()
        st.success(" Agent decided to do: {}.".format(",".join(stepActs)))
        st.success("RandomVacuumAgent is located at {} now.".format(a.location))
        st.info("Current Agent performance: {}.".format(a.performance))
        st.info("State of the Environment: {}.".format(e.status))
    else:
        st.error("Agent in location {} and it is dead.".format(a.location))
        
    image=getImg(a.location, e.status)
    st.image(image, caption="Agent is here", width="content")
        
    
    

        
    



def main():
        
    if "clicked" not in st.session_state:
        st.session_state["clicked"] = False
        
    if not st.session_state["clicked"]:
        # Set header title
        st.title('Simple Agents - lab2. Example1')
        st.header("_Initial Env._", divider=True)
        
        a1=RandomVacuumAgent()
        st.info(f"{a1} has the initial performance: {a1.performance}")
        
        e1 = TrivialVacuumEnvironment()
        # Check the initial state of the environment
        st.info("State of the Environment: {}.".format(e1.status))
        
        e1.add_thing(a1)
        
        image=getImg(a1.location, e1.status)  
        st.info("Agent in location {}.".format(a1.location))
            
        st.image(image, caption="Agent is here", width="content")
        
        drawBtn(e1,a1)
    
            
        
    if st.session_state["clicked"]:
        st.warning("Agent Step Done!")
        
    
    
    
        
        
        
                
            
    
    
    
    
    
    
if __name__ == '__main__':
    main()
    
    

