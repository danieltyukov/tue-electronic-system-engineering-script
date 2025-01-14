import subprocess
import os
import pandas as pd
import plotly.express as px

# Path to the Rotalumis executable
ROTALUMIS = os.path.expanduser("~/.p2/pool/plugins/nl.tue.rotalumis.executables_4.3.0.202310160813/linux/64bit/rotalumis")
MODEL_FILE = os.path.expanduser("~/eclipse-workspace/xcps/models/xcps-model.poosl")
TRACE_INI = os.path.expanduser("~/eclipse-workspace/xcps/models/trace.ini")

# Cost data
COMPONENT_COSTS = {
    "belt": {"slow": 510, "normal": 1029, "fast": 1744},
    "index": {"slow": 133, "normal": 634, "fast": 919},
    "gantry": {"slow": 798, "normal": 1299, "fast": 1529},
}

DEFAULT_MAKESPAN = 242
DEFAULT_PRICE = 6032.40
PRODUCTION_COST = 1000

# Parse makespan from Rotalumis output
def parse_makespan(output):
    makespan = -1
    for line in output.split("\n"):
        if "Makespan :" in line:
            makespan = float(line.split(":")[1].strip())
    return makespan

# Run simulation
def run_simulation(trace_ini, model_file):
    try:
        result = subprocess.run(
            [ROTALUMIS, "--stdlib", "-e", trace_ini, "--poosl", model_file],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return parse_makespan(result.stdout)
        else:
            print(f"Error: {result.stderr}")
            return -1
    except Exception as e:
        print(f"Error running simulation: {e}")
        return -1

# Calculate profit
def calculate_profit(bom_cost, makespan):
    price = 1.2 * (bom_cost + PRODUCTION_COST)
    volume = max(0, 1500 + 2 * (DEFAULT_PRICE - price) + 50 * (DEFAULT_MAKESPAN - makespan))
    revenue = price * volume
    return revenue - (bom_cost * volume)

# Main function to explore design space
def explore_design_space():
    results = []
    configurations = [
        {"belt": b, "index": i, "gantry": g}
        for b in ["slow", "normal", "fast"]
        for i in ["slow", "normal", "fast"]
        for g in ["slow", "normal", "fast"]
    ]

    for config in configurations:
        # Update the POOSL model file for the current configuration
        with open(MODEL_FILE, "r") as file:
            model_content = file.read()

        updated_model = model_content.replace("addSlowBelts", f"add{config['belt'].capitalize()}Belts") \
                                     .replace("addFastIndex", f"add{config['index'].capitalize()}Index") \
                                     .replace("addNormalArm1", f"add{config['gantry'].capitalize()}Arm1") \
                                     .replace("addNormalArm2", f"add{config['gantry'].capitalize()}Arm2")

        with open(MODEL_FILE, "w") as file:
            file.write(updated_model)

        # Run the simulation
        makespan = run_simulation(TRACE_INI, MODEL_FILE)
        if makespan < 0:
            continue

        # Calculate cost and profit
        bom_cost = COMPONENT_COSTS["belt"][config["belt"]] + \
                   COMPONENT_COSTS["index"][config["index"]] + \
                   2 * COMPONENT_COSTS["gantry"][config["gantry"]]
        profit = calculate_profit(bom_cost, makespan)

        results.append((config["belt"], config["index"], config["gantry"], makespan, profit))

    # Save results
    results_df = pd.DataFrame(results, columns=["Belt", "Index", "Gantry", "Makespan", "Profit"])
    results_df.to_csv("design_space_results.csv", index=False)

    # Plot results
    fig = px.scatter(results_df, x="Makespan", y="Profit", color="Belt", size="Profit", title="Design Space Exploration")
    fig.show()

if __name__ == "__main__":
    explore_design_space()
