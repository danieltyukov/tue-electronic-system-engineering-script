import subprocess
import os
import pandas as pd
import plotly.express as px

# Path to the Rotalumis executable
ROTALUMIS = os.path.expanduser("~/.p2/pool/plugins/nl.tue.rotalumis.executables_4.3.0.202310160813/linux/64bit/rotalumis")
MAKESPAN_PREFIX = "Makespan : "

# Parses the makespan from Rotalumis output
def parse_makespan(output):
    for line in output.split("\n"):
        if MAKESPAN_PREFIX in line:
            return float(line.split(MAKESPAN_PREFIX)[1].strip())
    return None

# Update POOSL model for a given configuration
def update_poosl_model(belt, index, gantry, model_path):
    with open(model_path, 'r') as file:
        data = file.readlines()
    
    # Modify parameters with correct capitalization
    for i, line in enumerate(data):
        if "addSlowBelts" in line or "addNormalBelts" in line or "addFastBelts" in line:
            data[i] = f"        add{belt.capitalize()}Belts\n"
        if "addSlowIndex" in line or "addNormalIndex" in line or "addFastIndex" in line:
            data[i] = f"        add{index.capitalize()}Index\n"
        if "addSlowArm1" in line or "addNormalArm1" in line or "addFastArm1" in line:
            data[i] = f"        add{gantry.capitalize()}Arm1\n"
        if "addSlowArm2" in line or "addNormalArm2" in line or "addFastArm2" in line:
            data[i] = f"        add{gantry.capitalize()}Arm2\n"
    
    with open(model_path, 'w') as file:
        file.writelines(data)

# Run the performance model using trace.ini and a POOSL model
def run_performance_model(trace_ini, model):
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

# Calculate profit and loss
def calculate_profit_and_loss(price, volume, bom_cost):
    revenue = volume * price
    total_cost = bom_cost + 1000  # Add fixed costs (e.g., NRE)
    profit = revenue - total_cost
    loss = total_cost if volume == 0 else 0
    return profit, loss

# Main execution
if __name__ == "__main__":
    trace_ini_path = os.path.expanduser("~/eclipse-workspace/xcps/models/trace.ini")
    model_file = os.path.expanduser("~/eclipse-workspace/xcps/models/xcps-model.poosl")
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
    for belt, index, gantry in configurations:
        print(f"Testing configuration: Belt={belt}, Index={index}, Gantry={gantry}")
        update_poosl_model(belt, index, gantry, model_file)
        makespan = run_performance_model(trace_ini_path, model_file)
        
        if makespan:
            price = 1.2 * (2239 + 1000)  # Adjust BOM and NRE as needed
            volume = max(0, 1500 + 2 * (6032.4 - price) + 50 * (242 - makespan))
            profit, loss = calculate_profit_and_loss(price, volume, 2239)
            results.append((belt, index, gantry, makespan, profit, loss))
            print(f"Configuration result: Makespan={makespan}, Profit={profit}, Loss={loss}")
        else:
            print(f"Failed to simulate configuration: Belt={belt}, Index={index}, Gantry={gantry}")

    # Save results to CSV
    output_csv = "design_space_results.csv"
    df = pd.DataFrame(results, columns=["Belt", "Index", "Gantry", "Makespan", "Profit", "Loss"])
    df.to_csv(output_csv, index=False)
    print(f"Results saved to {output_csv}")

    # Visualization
    df['Configuration'] = df[['Belt', 'Index', 'Gantry']].agg('-'.join, axis=1)
    fig = px.scatter(
        df,
        x="Makespan",
        y="Profit",
        color="Configuration",
        size="Profit",
        title="Makespan vs Profit for Configurations",
        labels={"Makespan": "Makespan (s)", "Profit": "Profit ($)"},
    )
    fig.show()
