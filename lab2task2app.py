# lab2task2app.py  — Streamlit UI for Task 2 (Table-Driven Cat)
# Place this file at the project root (outside src/)
import streamlit as st
from datetime import datetime

from src.catFriendlyHouseEnvironmentClass import CatFriendlyHouse
from src.agents import TableDrivenCatAgent
from src.foodClass import Milk, Sausage

APP_TITLE = "Lab 2 — Task 2: Table-Driven Cat (Cat-Friendly-House)"


# ---------------------- helpers ----------------------
def format_rooms(env: CatFriendlyHouse):
    a = env.show_world()["A"]
    b = env.show_world()["B"]
    return a, b


def status_badge(txt: str):
    if txt.startswith("Milk"):
        return f"🍼 {txt}"
    if txt.startswith("Sausage"):
        return f"🌭 {txt}"
    return "⬜ Empty"


def location_label(loc: tuple):
    return "A" if loc == (0, 0) else "B"


def ensure_state():
    if "env" not in st.session_state:
        st.session_state.env = CatFriendlyHouse()
    if "cat" not in st.session_state:
        st.session_state.cat = TableDrivenCatAgent()
        st.session_state.env.add_thing(st.session_state.cat)
    if "step" not in st.session_state:
        st.session_state.step = 0
    if "log" not in st.session_state:
        st.session_state.log = []


def append_log(percept, action, env: CatFriendlyHouse, cat):
    st.session_state.step += 1
    entry = {
        "step": st.session_state.step,
        "percept": percept,
        "action": action,
        "after_loc": cat.location,
        "after_perf": cat.performance,
        "rooms": env.show_world(),
        "time": datetime.now().strftime("%H:%M:%S"),
    }
    st.session_state.log.append(entry)


def do_one_step():
    env = st.session_state.env
    cat = st.session_state.cat
    percept = env.percept(cat)
    action = cat(percept)  # table-driven program
    env.execute_action(cat, action)
    append_log(percept, action, env, cat)


def reset_world():
    st.session_state.clear()
    ensure_state()


# ---------------------- UI ----------------------
st.set_page_config(page_title=APP_TITLE, page_icon="🐈", layout="wide")
ensure_state()

st.title(APP_TITLE)
st.caption(
    "Two-room world with one Milk and one Sausage in different rooms. "
    "Cat is a table-driven agent using condition→action rules."
)

# Controls
left, mid, right = st.columns([1, 1, 2])
with left:
    if st.button("▶️ Step"):
        if not st.session_state.env.done():
            do_one_step()
with mid:
    if st.button("⏭ Run until done (max 20 steps)"):
        count = 0
        while not st.session_state.env.done() and count < 20:
            do_one_step()
            count += 1
with right:
    if st.button("🔄 Reset"):
        reset_world()

st.divider()

# World snapshot
env = st.session_state.env
cat = st.session_state.cat
roomA, roomB = format_rooms(env)

c1, c2, c3, c4 = st.columns([1.1, 1.1, 1, 1.5])

with c1:
    st.subheader("Room A")
    st.write(status_badge(roomA))

with c2:
    st.subheader("Room B")
    st.write(status_badge(roomB))

with c3:
    st.subheader("Cat")
    st.metric("Location", location_label(cat.location))
    st.metric("Performance", cat.performance)

with c4:
    st.subheader("Food Constants")
    st.write(f"Milk calories: **{Milk.CALORIES}**")
    st.write(f"Sausage calories: **{Sausage.CALORIES}**")
    st.caption(
        "You can change these in `src/foodClass.py` if your instructor uses different values."
    )

# Finished banner
if env.done():
    st.success("Environment done: both items consumed ✅")

st.divider()

# Log
st.subheader("Step Log")
if st.session_state.log:
    for row in reversed(st.session_state.log):
        with st.expander(
            f"Step {row['step']} — action: {row['action']} — perf: {row['after_perf']} — {row['time']}",
            expanded=False,
        ):
            st.write(f"**Percept** → {row['percept']}")
            st.write(
                f"**After** → location={row['after_loc']}, performance={row['after_perf']}"
            )
            st.write(f"**Rooms** → {row['rooms']}")
else:
    st.info("No steps yet. Click **Step** or **Run until done**.")

st.caption(
    "Tip: Movement costs -1. Drinking/Eating updates performance via the cat’s methods (`AgentCat.drink/eat`)."
)
