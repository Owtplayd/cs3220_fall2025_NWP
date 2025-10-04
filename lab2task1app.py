# lab2task1_app.py
"""
Streamlit app for Task 1: Crazy House (Cat, Mouse, Milk, Dog).
Run with:
    streamlit run lab2task1_app.py
"""

import random
import streamlit as st
from typing import List, Dict, Any

# ---- your course modules ----
from src.environmentProClass import environmentPro, Mouse, Milk, Dog
from src.agents import RandomCrazyHouseCat


# ---------------------- UI helpers ----------------------
def prettify_env(env: environmentPro) -> str:
    lines = []
    for i, room in enumerate(env.rooms):
        stuff = ",".join(t.__class__.__name__ for t in room) or "Empty"
        lines.append(f"Room {i}: {stuff}")
    return "\n".join(lines)


def step_once(env: environmentPro, cat, history: List[Dict[str, Any]]) -> None:
    """Execute one agent decision step and record it into history."""
    if not cat.alive:
        return
    percept = env.percept(cat)  # (room_idx, tuple(things))
    action = cat(percept)  # random action from allowed list
    env.execute_action(cat, action)  # apply environment transition

    history.append(
        {
            "percept_room": percept[0],
            "percept_sees": list(percept[1]),
            "action": action,
            "post_location": cat.location,
            "post_perf": cat.performance,
            "alive": cat.alive,
        }
    )


def init_sim(seed: int, n_rooms: int, start_perf: int):
    """Create a fresh environment + agent + initial placement under constraints."""
    if seed:
        random.seed(int(seed))

    env = environmentPro(n_rooms=n_rooms)

    # place things randomly (constraints are enforced in add_thing)
    env.add_thing(Mouse())
    env.add_thing(Milk())
    env.add_thing(Dog())

    # place cat in random room
    cat = RandomCrazyHouseCat(start_perf=start_perf, name="Cat")
    env.add_thing(cat)

    return env, cat


# ---------------------- Streamlit UI ----------------------
st.set_page_config(page_title="Crazy House — Task 1", layout="wide")
st.title("🐱 Crazy House — Task 1")
st.caption("Cat randomly chooses among: MoveRight, MoveLeft, Eat, Drink, Fight.")

# Sidebar controls
with st.sidebar:
    st.header("Simulation Settings")
    n_rooms = st.slider("Number of rooms", min_value=2, max_value=10, value=5, step=1)
    start_perf = st.number_input("Cat starting performance", value=0, step=1)
    seed = st.number_input("Random seed (0 = off)", value=0, step=1)
    auto_steps = st.slider("Run N steps (for 'Run' button)", 1, 200, 20)

    colA, colB, colC = st.columns(3)
    with colA:
        reset_btn = st.button("Reset", type="secondary")
    with colB:
        step_btn = st.button("Step")
    with colC:
        run_btn = st.button("Run", type="primary")

# Session state init
if "env" not in st.session_state:
    st.session_state.env, st.session_state.cat = init_sim(seed, n_rooms, start_perf)
    st.session_state.history = []
    st.session_state.meta = {
        "seed": int(seed),
        "n_rooms": int(n_rooms),
        "start_perf": int(start_perf),
    }

# Handle resets / parameter changes
params_changed = (
    st.session_state.meta["seed"] != int(seed)
    or st.session_state.meta["n_rooms"] != int(n_rooms)
    or st.session_state.meta["start_perf"] != int(start_perf)
)

if reset_btn or params_changed:
    st.session_state.env, st.session_state.cat = init_sim(seed, n_rooms, start_perf)
    st.session_state.history = []
    st.session_state.meta.update(
        {"seed": int(seed), "n_rooms": int(n_rooms), "start_perf": int(start_perf)}
    )

# Main columns
left, right = st.columns([1.2, 1])

with left:
    st.subheader("House")
    st.code(prettify_env(st.session_state.env))

    cat = st.session_state.cat
    st.markdown(
        f"""
**Cat**  
- Location: `{cat.location}`  
- Performance: `{cat.performance}`  
- Alive: `{cat.alive}`  
"""
    )

    # Controls
    if step_btn and st.session_state.cat.alive:
        step_once(st.session_state.env, st.session_state.cat, st.session_state.history)

    if run_btn and st.session_state.cat.alive:
        for _ in range(auto_steps):
            if not st.session_state.cat.alive:
                break
            step_once(
                st.session_state.env, st.session_state.cat, st.session_state.history
            )

    # After actions, show updated env and cat
    st.markdown("### After Step / Run")
    st.code(prettify_env(st.session_state.env))
    st.markdown(
        f"""
**Cat (now)**  
- Location: `{cat.location}`  
- Performance: `{cat.performance}`  
- Alive: `{cat.alive}`  
"""
    )

with right:
    st.subheader("Step Log")
    if not st.session_state.history:
        st.info("No steps yet. Click **Step** or **Run** to start.")
    else:
        for i, h in enumerate(st.session_state.history, start=1):
            st.markdown(f"**Step {i}**")
            st.write(f"Percept → room={h['percept_room']}, sees={h['percept_sees']}")
            st.write(f"Action  → {h['action']}")
            st.write(
                f"After   → location={h['post_location']}, perf={h['post_perf']}, alive={h['alive']}"
            )
            st.divider()

# Footer: rule recap (for your professor)
with st.expander("Show rules & grading cheatsheet"):
    st.markdown(
        """
- **Placement constraints**  
  - Mouse + Milk in same room → keep **Mouse**, remove **Milk**.  
  - Mouse + Dog in same room → move **Mouse** randomly to **previous or next** room (bounded).  
  - Dog + Milk may co-exist.  

- **Agent** (random, oblivious to state): `MoveRight`, `MoveLeft`, `Eat`, `Drink`, `Fight`  

- **Rewards / Penalties**  
  - Drink: **+5** (milk removed)  
  - Eat: **+10** if performance **≥ 3** (mouse removed)  
  - Move: **−1**  
  - Fight vs Dog: **win if performance ≥ 10** → **+20**, else **−10**  
  - **Game over if performance ≤ 0**
        """
    )
