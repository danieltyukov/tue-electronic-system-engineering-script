import subprocess
import os
import pandas as pd
import plotly.express as px

# ----------------------------------------------------------------------------
# USER-CONFIGURABLE PATHS
# ----------------------------------------------------------------------------
ROTALUMIS = os.path.expanduser("~/.p2/pool/plugins/nl.tue.rotalumis.executables_4.3.0.202310160813/linux/64bit/rotalumis")
trace_ini_path = os.path.expanduser("~/eclipse-workspace/xcps/models/trace.ini")
model_file = os.path.expanduser("~/eclipse-workspace/xcps/models/xcps-model.poosl")

# Constants for parsing
MAKESPAN_PREFIX = "Makespan : "

# ----------------------------------------------------------------------------
# FUNCTION: parse_makespan
# ----------------------------------------------------------------------------
def parse_makespan(output):
    """
    Parses the Rotalumis console output for the 'Makespan : <value>' line,
    returning that value as a float or None if not found.
    """
    for line in output.split("\n"):
        if MAKESPAN_PREFIX in line:
            try:
                return float(line.split(MAKESPAN_PREFIX)[1].strip())
            except ValueError:
                return None
    return None

# ----------------------------------------------------------------------------
# FUNCTION: update_poosl_model
# ----------------------------------------------------------------------------
def update_poosl_model(belt, index, gantry, model_path):
    """
    Edits the xcps-model.poosl file, replacing the addXXX methods with the new
    'belt', 'index', and 'gantry' parameters.
    """
    with open(model_path, 'r') as file:
        data = file.readlines()
    
    for i, line in enumerate(data):
        # Belt
        if "addSlowBelts" in line or "addNormalBelts" in line or "addFastBelts" in line:
            data[i] = f"        add{belt.capitalize()}Belts\n"
        # Index
        if "addSlowIndex" in line or "addNormalIndex" in line or "addFastIndex" in line:
            data[i] = f"        add{index.capitalize()}Index\n"
        # Gantry
        if "addSlowArm1" in line or "addNormalArm1" in line or "addFastArm1" in line:
            data[i] = f"        add{gantry.capitalize()}Arm1\n"
        if "addSlowArm2" in line or "addNormalArm2" in line or "addFastArm2" in line:
            data[i] = f"        add{gantry.capitalize()}Arm2\n"
    
    with open(model_path, 'w') as file:
        file.writelines(data)

# ----------------------------------------------------------------------------
# FUNCTION: run_performance_model
# ----------------------------------------------------------------------------
def run_performance_model(trace_ini, model):
    """
    Invokes Rotalumis on the given model and trace.ini configuration, returning
    the parsed makespan or None if not found.
    """
    try:
        proc = subprocess.run(
            [ROTALUMIS, "--stdlib", "-e", trace_ini, "--poosl", model],
            capture_output=True,
            text=True
        )
        if proc.returncode == 0:
            return parse_makespan(proc.stdout)
        else:
            print(f"Error running model {model}: {proc.stderr}")
            return None
    except FileNotFoundError:
        print("Rotalumis executable not found. Please check the path.")
        return None

# ----------------------------------------------------------------------------
# FUNCTION: calculate_profit_and_loss
# ----------------------------------------------------------------------------
def calculate_profit_and_loss(price, volume, bom_cost):
    """
    Returns (profit, loss).
    For demonstration, 'loss' is forced to 0 if volume>0, otherwise cost if volume=0.
    """
    revenue = volume * price
    total_cost = bom_cost + 1000  # Add a fixed cost (like an NRE).
    profit = revenue - total_cost
    loss = total_cost if volume == 0 else 0
    return profit, loss

# ----------------------------------------------------------------------------
# MAIN SCRIPT
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    # All possible combinations
    configurations = [
        ("slow", "slow", "slow"),
        ("slow", "slow", "normal"),
        ("slow", "slow", "fast"),
        ("slow", "normal", "slow"),
        ("slow", "normal", "normal"),
        ("slow", "normal", "fast"),
        ("slow", "fast", "slow"),
        ("slow", "fast", "normal"),
        ("slow", "fast", "fast"),
        ("normal", "slow", "slow"),
        ("normal", "slow", "normal"),
        ("normal", "slow", "fast"),
        ("normal", "normal", "slow"),
        ("normal", "normal", "normal"),
        ("normal", "normal", "fast"),
        ("normal", "fast", "slow"),
        ("normal", "fast", "normal"),
        ("normal", "fast", "fast"),
        ("fast", "slow", "slow"),
        ("fast", "slow", "normal"),
        ("fast", "slow", "fast"),
        ("fast", "normal", "slow"),
        ("fast", "normal", "normal"),
        ("fast", "normal", "fast"),
        ("fast", "fast", "slow"),
        ("fast", "fast", "normal"),
        ("fast", "fast", "fast")
    ]

    results = []

    # Run each configuration
    for belt, index, gantry in configurations:
        print(f"Testing configuration: Belt={belt}, Index={index}, Gantry={gantry}")
        update_poosl_model(belt, index, gantry, model_file)
        makespan = run_performance_model(trace_ini_path, model_file)
        
        if makespan:
            # Example price
            price = 1.2 * (2239 + 1000)  # e.g., BOM=2239, plus 1000 fixed => markup
            # Example demand function
            volume = max(0, 1500 + 2*(6032.4 - price) + 50*(242 - makespan))
            profit, loss = calculate_profit_and_loss(price, volume, 2239)
            results.append((belt, index, gantry, makespan, profit, loss))
            print(f"Configuration result: Makespan={makespan}, Profit={profit}, Loss={loss}")
        else:
            print(f"Failed to simulate configuration: Belt={belt}, Index={index}, Gantry={gantry}")

    # Convert results to a DataFrame and save
    df = pd.DataFrame(
        results,
        columns=["BeltSpeed", "IndexSpeed", "GantrySpeed", "Makespan", "Profit", "Loss"]
    )
    output_csv = "design_space_results.csv"
    df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")

    # Create a single column that describes the config more clearly
    df["Configuration"] = df.apply(
        lambda row: f"Belt={row['BeltSpeed']}, Index={row['IndexSpeed']}, Gantry={row['GantrySpeed']}",
        axis=1
    )

    # ----------------------------------------------------------------------------
    # PLOT: Makespan vs Profit (Scatter) with color showing the configuration
    # ----------------------------------------------------------------------------
    fig = px.scatter(
        df,
        x="Makespan",
        y="Profit",
        color="Configuration",
        size="Profit",
        title="Makespan vs Profit across Configurations",
        labels={"Makespan": "Makespan (s)", "Profit": "Profit ($)"}
    )
    fig.update_layout(
        xaxis_title="Makespan (seconds)",
        yaxis_title="Profit (USD)",
        legend_title_text="Configuration",
    )
    fig.show()

    print("\nNotes:")
    print("1) 'Failed to simulate' often means the model reached a deadlock or never printed a final Makespan.")
    print("2) Profits can appear always positive under these parameters. Adjust BOM/price/demand if needed.")
