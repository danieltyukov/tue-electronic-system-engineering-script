import subprocess
import os
import pandas as pd
import plotly.express as px
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Paths to Rotalumis and POOSL files
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
    for line in output.split("\n"):
        if "Makespan :" in line:
            return float(line.split(":")[1].strip())
    return -1

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
            logging.error(f"Simulation error: {result.stderr}")
            return -1
    except Exception as e:
        logging.error(f"Error running simulation: {e}")
        return -1

# Calculate profit
def calculate_profit(bom_cost, makespan):
    price = 1.2 * (bom_cost + PRODUCTION_COST)
    volume = max(0, 1500 + 2 * (DEFAULT_PRICE - price) + 50 * (DEFAULT_MAKESPAN - makespan))
    revenue = price * volume
    print("price: ", price, "volume: ", volume, "revenue: ", revenue, "bom_cost: ", bom_cost, "profit: ", revenue - (bom_cost * volume))
    return revenue - (bom_cost * volume)

# Update model file for a specific configuration
def update_model_file(model_file, belt, index, gantry):
    with open(model_file, "r") as file:
        model_content = file.read()
    updated_model = model_content.replace("addSlowBelts", f"add{belt.capitalize()}Belts") \
                                 .replace("addFastIndex", f"add{index.capitalize()}Index") \
                                 .replace("addNormalArm1", f"add{gantry.capitalize()}Arm1") \
                                 .replace("addNormalArm2", f"add{gantry.capitalize()}Arm2")
    with open(model_file, "w") as file:
        file.write(updated_model)

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
        logging.info(f"Testing configuration: Belt={config['belt']}, Index={config['index']}, Gantry={config['gantry']}")

        # Update the POOSL model file
        update_model_file(MODEL_FILE, config['belt'], config['index'], config['gantry'])

        # Run simulation
        makespan = run_simulation(TRACE_INI, MODEL_FILE)
        if makespan < 0:
            logging.warning("Simulation failed, skipping this configuration.")
            continue

        # Calculate cost and profit
        bom_cost = COMPONENT_COSTS["belt"][config["belt"]] + \
                   COMPONENT_COSTS["index"][config["index"]] + \
                   2 * COMPONENT_COSTS["gantry"][config["gantry"]]
        profit = calculate_profit(bom_cost, makespan)
        results.append((config['belt'], config['index'], config['gantry'], makespan, profit))

        logging.info(f"Configuration result: Makespan={makespan}, Profit={profit}")

    # Save results
    results_df = pd.DataFrame(results, columns=["Belt", "Index", "Gantry", "Makespan", "Profit"])
    results_df.to_csv("design_space_results.csv", index=False)
    logging.info("Results saved to design_space_results.csv")

    # Enhanced visualization
    fig = px.scatter(
        results_df,
        x="Makespan",
        y="Profit",
        color="Belt",
        symbol="Index",
        size="Profit",
        facet_col="Gantry",
        title="Design Space Exploration",
        labels={"Profit": "Profit (€)", "Makespan": "Makespan (s)"}
    )
    fig.add_hline(y=0, line_dash="dash", annotation_text="Break-even", annotation_position="top left")
    fig.show()

if __name__ == "__main__":
    explore_design_space()
