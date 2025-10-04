from src.locations import loc_A, loc_B

actionList = ["Right", "Left", "Suck", "NoOp"]

table = {
    ((loc_A, "Clean"),): "Right",
    ((loc_A, "Dirty"),): "Suck",
    ((loc_B, "Clean"),): "Left",
    ((loc_B, "Dirty"),): "Suck",
    ((loc_A, "Dirty"), (loc_A, "Clean")): "Right",
    ((loc_A, "Clean"), (loc_B, "Dirty")): "Suck",
    ((loc_B, "Clean"), (loc_A, "Dirty")): "Suck",
    ((loc_B, "Dirty"), (loc_B, "Clean")): "Left",
    ((loc_A, "Dirty"), (loc_A, "Clean"), (loc_B, "Dirty")): "Suck",
    ((loc_B, "Dirty"), (loc_B, "Clean"), (loc_A, "Dirty")): "Suck",
}

# Vacuum reflex rules
vacuumRules = {
    ((0, 0), "Dirty"): "Suck",
    ((1, 0), "Dirty"): "Suck",
    ((0, 0), "Clean"): "Right",
    ((1, 0), "Clean"): "Left",
}

# Rules for your Task3 (left unchanged)
a2proRules = {
    "Office manager": "Give mail",
    "IT": "Give donuts",
    "Student": "Give pizza",
    "Clear": "Go ahead",
    "Last room": "Stop",
}

# -------------------- Crazy House (Task 1) --------------------
# Action list for the Cat in Crazy House:
crazy_house_actions = ["MoveRight", "MoveLeft", "Eat", "Drink", "Fight"]
