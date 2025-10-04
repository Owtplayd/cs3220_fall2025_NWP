# run_task2_cat.py  (place this file at repo root, NOT inside src/)
from pprint import pprint

from src.catFriendlyHouseEnvironmentClass import CatFriendlyHouse
from src.agents import TableDrivenCatAgent


def run(steps: int = 12):
    env = CatFriendlyHouse()
    cat = TableDrivenCatAgent()

    env.add_thing(cat)  # random A/B start

    print("=== Cat-Friendly-House / Task 2 ===")
    print("Initial world:", env.show_world())
    print(f"Cat starts at {cat.location}, perf={cat.performance}")

    for i in range(1, steps + 1):
        percept = env.percept(cat)
        action = cat(percept)  # table-driven program
        env.execute_action(cat, action)

        print(f"\nStep {i}:")
        print(f"  Percept -> {percept}")
        print(f"  Action  -> {action}")
        print(
            f"  After   -> location={cat.location}, perf={cat.performance}, alive={cat.alive}"
        )
        print(f"  Rooms   -> {env.show_world()}")

        if env.done():
            print("\nEnvironment done: both items consumed.")
            break

    print("\n=== Finished ===")
    print(f"Final -> location={cat.location}, perf={cat.performance}")
    print("Final world:", env.show_world())


if __name__ == "__main__":
    run()
