# quick_run_crazy_house.py
from src.environmentProClass import environmentPro, Mouse, Milk, Dog
from src.agents import RandomCrazyHouseCat

STEPS = 20  # number of decision steps to run
START_PERF = 5  # set >0 if you want to start stronger


def pretty_env(env):
    lines = []
    for i, room in enumerate(env.rooms):
        stuff = ",".join(t.__class__.__name__ for t in room) or "Empty"
        lines.append(f"  Room {i}: {stuff}")
    return "\n".join(lines)


def main():
    env = environmentPro(n_rooms=5)

    # place things randomly (constraints are applied inside add_thing)
    env.add_thing(Mouse())
    env.add_thing(Milk())
    env.add_thing(Dog())

    # cat in random room
    cat = RandomCrazyHouseCat(start_perf=START_PERF, name="Cat")
    env.add_thing(cat)

    print("Initial House:")
    print(pretty_env(env))
    print(f"Cat starts in room {cat.location}, perf={cat.performance}\n")

    for step in range(1, STEPS + 1):
        if not cat.alive:
            print(f"Cat is dead. Stopping at step {step}.")
            break

        percept = env.percept(cat)
        action = cat(percept)  # random choice from available actions

        print(f"Step {step}:")
        print(f"  Percept -> room={percept[0]}, sees={list(percept[1])}")
        print(f"  Action  -> {action}")

        env.execute_action(cat, action)

        print(
            f"  After   -> location={cat.location}, perf={cat.performance}, alive={cat.alive}"
        )
        print(pretty_env(env))
        print("-" * 50)


if __name__ == "__main__":
    main()
