# src/rules_cat.py
from src.locations import loc_A, loc_B

# Available actions for Cat-Friendly-House
cat_actions = ["MoveRight", "MoveLeft", "Drink", "Eat"]

# Table-driven rules for the Cat (Task 2)
# Keys are tuples of percepts seen so far, each percept is (location, status)
# Status ∈ {'MilkHere', 'SausageHere', 'Empty'}
feedingRules = {
    # --- single-percept rules ---
    ((loc_A, "MilkHere"),): "Drink",
    ((loc_A, "SausageHere"),): "Eat",
    ((loc_A, "Empty"),): "MoveRight",
    ((loc_B, "MilkHere"),): "Drink",
    ((loc_B, "SausageHere"),): "Eat",
    ((loc_B, "Empty"),): "MoveLeft",
    # --- short histories to keep moving after consuming ---
    ((loc_A, "MilkHere"), (loc_A, "Empty")): "MoveRight",
    ((loc_A, "SausageHere"), (loc_A, "Empty")): "MoveRight",
    ((loc_B, "MilkHere"), (loc_B, "Empty")): "MoveLeft",
    ((loc_B, "SausageHere"), (loc_B, "Empty")): "MoveLeft",
    # --- when we come to the other room and find the remaining item ---
    ((loc_A, "Empty"), (loc_B, "MilkHere")): "Drink",
    ((loc_A, "Empty"), (loc_B, "SausageHere")): "Eat",
    ((loc_B, "Empty"), (loc_A, "MilkHere")): "Drink",
    ((loc_B, "Empty"), (loc_A, "SausageHere")): "Eat",
    # --- keep moving if still empty on arrival ---
    ((loc_A, "Empty"), (loc_B, "Empty")): "MoveLeft",
    ((loc_B, "Empty"), (loc_A, "Empty")): "MoveRight",
}
