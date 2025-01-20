import subprocess
import os
import pandas as pd
import plotly.express as px

ROTALUMIS = os.path.expanduser("~/.p2/pool/plugins/nl.tue.rotalumis.executables_4.3.0.202310160813/linux/64bit/rotalumis")
trace_ini_path = os.path.expanduser("~/eclipse-workspace/xcps/models/trace.ini")
model_file = os.path.expanduser("~/eclipse-workspace/xcps/models/xcps-model.poosl")

MAKESPAN_PREFIX = "Makespan : "


def parse_makespan(output):
    for line in output.split("\n"):
        if MAKESPAN_PREFIX in line:
            try:
                return float(line.split(MAKESPAN_PREFIX)[1].strip())
            except ValueError:
                return None
    return None


def update_poosl_model(belt, index, gantry1, gantry2, model_path):
    with open(model_path, 'r') as file:
        data = file.readlines()

    for i, line in enumerate(data):
        if "addSlowBelts" in line or "addNormalBelts" in line or "addFastBelts" in line:
            data[i] = f"        add{belt.capitalize()}Belts\n"
        if "addSlowIndex" in line or "addNormalIndex" in line or "addFastIndex" in line:
            data[i] = f"        add{index.capitalize()}Index\n"
        if "addSlowArm1" in line or "addNormalArm1" in line or "addFastArm1" in line:
            data[i] = f"        add{gantry1.capitalize()}Arm1\n"
        if "addSlowArm2" in line or "addNormalArm2" in line or "addFastArm2" in line:
            data[i] = f"        add{gantry2.capitalize()}Arm2\n"

    with open(model_path, 'w') as file:
        file.writelines(data)


def run_performance_model(trace_ini, model):
    try:
        proc = subprocess.run(
            [ROTALUMIS, "--stdlib", "-e", trace_ini, "--poosl", model],
            capture_output=True,
            text=True
        )
        return parse_makespan(proc.stdout) if proc.returncode == 0 else None
    except FileNotFoundError:
        return None


def calculate_profit(makespan, belt, index, gantry1, gantry2, adjustments):
    make0, window, price0 = 242, 913, 6032.4
    default_belt, default_index, default_gantry1, default_gantry2 = 's', 'f', 'n', 'n'

    if (belt != default_belt, index != default_index, gantry1 != default_gantry1, gantry2 != default_gantry2):
        changes = 1
    else:
        changes = 0

    # changes = sum([belt != default_belt, index != default_index, gantry != default_gantry])
    delay = adjustments * 28 + changes * 56

    cost_map = {
        'belt': {'s': 510, 'n': 1029, 'f': 1744},
        'index': {'s': 133, 'n': 634, 'f': 919},
        'gantry1': {'s': 798, 'n': 1299, 'f': 1529},
        'gantry2': {'s': 798, 'n': 1299, 'f': 1529}
    }

    bom_cost = (cost_map['belt'][belt] + cost_map['index'][index] + cost_map['gantry1'][gantry1] + cost_map['gantry2'][gantry2])
    price = 1.2 * (bom_cost + 1000)
    volume = max(0, 1500 + 2 * (price0 - price) + 50 * (make0 - makespan))

    if volume > 0:
        volume *= 1 - ((3 * window - delay) * delay / (2 * window ** 2))

    cost = bom_cost * volume + 72000 * adjustments + 108000 * changes
    profit = price * volume - cost

    return profit


if __name__ == "__main__":
    configurations = [
        ("slow", "slow", "slow", "slow"),
        ("slow", "slow", "slow", "normal"),
        ("slow", "slow", "slow", "fast"),
        ("slow", "slow", "normal", "slow"),
        ("slow", "slow", "normal", "normal"),
        ("slow", "slow", "normal", "fast"),
        ("slow", "slow", "fast", "slow"),
        ("slow", "slow", "fast", "normal"),
        ("slow", "slow", "fast", "fast"),
        ("slow", "normal", "slow", "slow"),
        ("slow", "normal", "slow", "normal"),
        ("slow", "normal", "slow", "fast"),
        ("slow", "normal", "normal", "slow"),
        ("slow", "normal", "normal", "normal"),
        ("slow", "normal", "normal", "fast"),
        ("slow", "normal", "fast", "slow"),
        ("slow", "normal", "fast", "normal"),
        ("slow", "normal", "fast", "fast"),
        ("slow", "fast", "slow", "slow"),
        ("slow", "fast", "slow", "normal"),
        ("slow", "fast", "slow", "fast"),
        ("slow", "fast", "normal", "slow"),
        ("slow", "fast", "normal", "normal"),
        ("slow", "fast", "normal", "fast"),
        ("slow", "fast", "fast", "slow"),
        ("slow", "fast", "fast", "normal"),
        ("slow", "fast", "fast", "fast"),
        ("normal", "slow", "slow", "slow"),
        ("normal", "slow", "slow", "normal"),
        ("normal", "slow", "slow", "fast"),
        ("normal", "slow", "normal", "slow"),
        ("normal", "slow", "normal", "normal"),
        ("normal", "slow", "normal", "fast"),
        ("normal", "slow", "fast", "slow"),
        ("normal", "slow", "fast", "normal"),
        ("normal", "slow", "fast", "fast"),
        ("normal", "normal", "slow", "slow"),
        ("normal", "normal", "slow", "normal"),
        ("normal", "normal", "slow", "fast"),
        ("normal", "normal", "normal", "slow"),
        ("normal", "normal", "normal", "normal"),
        ("normal", "normal", "normal", "fast"),
        ("normal", "normal", "fast", "slow"),
        ("normal", "normal", "fast", "normal"),
        ("normal", "normal", "fast", "fast"),
        ("normal", "fast", "slow", "slow"),
        ("normal", "fast", "slow", "normal"),
        ("normal", "fast", "slow", "fast"),
        ("normal", "fast", "normal", "slow"),
        ("normal", "fast", "normal", "normal"),
        ("normal", "fast", "normal", "fast"),
        ("normal", "fast", "fast", "slow"),
        ("normal", "fast", "fast", "normal"),
        ("normal", "fast", "fast", "fast"),
        ("fast", "slow", "slow", "slow"),
        ("fast", "slow", "slow", "normal"),
        ("fast", "slow", "slow", "fast"),
        ("fast", "slow", "normal", "slow"),
        ("fast", "slow", "normal", "normal"),
        ("fast", "slow", "normal", "fast"),
        ("fast", "slow", "fast", "slow"),
        ("fast", "slow", "fast", "normal"),
        ("fast", "slow", "fast", "fast"),
        ("fast", "normal", "slow", "slow"),
        ("fast", "normal", "slow", "normal"),
        ("fast", "normal", "slow", "fast"),
        ("fast", "normal", "normal", "slow"),
        ("fast", "normal", "normal", "normal"),
        ("fast", "normal", "normal", "fast"),
        ("fast", "normal", "fast", "slow"),
        ("fast", "normal", "fast", "normal"),
        ("fast", "normal", "fast", "fast"),
        ("fast", "fast", "slow", "slow"),
        ("fast", "fast", "slow", "normal"),
        ("fast", "fast", "slow", "fast"),
        ("fast", "fast", "normal", "slow"),
        ("fast", "fast", "normal", "normal"),
        ("fast", "fast", "normal", "fast"),
        ("fast", "fast", "fast", "slow"),
        ("fast", "fast", "fast", "normal"),
        ("fast", "fast", "fast", "fast")
    ]

    results = []

    for belt, index, gantry1, gantry2 in configurations:
        update_poosl_model(belt, index, gantry1, gantry2, model_file)
        makespan = run_performance_model(trace_ini_path, model_file)

        if makespan:
            profit = calculate_profit(makespan, belt[0], index[0], gantry1[0], gantry2[0], adjustments=1)
            results.append((belt, index, gantry1, gantry2, makespan, profit))
            print(f"Configuration: Belt={belt}, Index={index}, Gantry1={gantry1}, Gantry2={gantry2} | Makespan: {makespan:.2f}, Profit: {profit:.2f}")

    df = pd.DataFrame(results, columns=["BeltSpeed", "IndexSpeed", "GantrySpeed1", "GantrySpeed2", "Makespan", "Profit"])
    df["Configuration"] = df.apply(lambda row: f"Belt={row['BeltSpeed']}, Index={row['IndexSpeed']}, Gantry1={row['GantrySpeed1']}, Gantry2={row['GantrySpeed2']}", axis=1)
    df.to_csv("design_space_results.csv", index=False)

    fig = px.scatter(
        df, x="Makespan", y="Profit", color="Configuration", title="Makespan vs Profit",
        labels={"Makespan": "Makespan (s)", "Profit": "Profit ($)"}
    )
    fig.show()
