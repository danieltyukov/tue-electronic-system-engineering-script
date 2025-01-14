import subprocess
import os
import pandas as pd
import plotly.express as px

# Path to the Rotalumis executable
ROTALUMIS = os.path.expanduser("~/.p2/pool/plugins/nl.tue.rotalumis.executables_4.3.0.202310160813/linux/64bit/rotalumis")
MAKESPAN_PREFIX = "Makespan : "

# Parses the makespan from Rotalumis output
def parse_makespan(output):
    makespan = -1
    for line in output.split("\n"):
        line = line.strip()
        idx = line.find(MAKESPAN_PREFIX)
        if idx >= 0:
            makespan = float(line[idx + len(MAKESPAN_PREFIX):])
    return makespan

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
            return -1
    except FileNotFoundError:
        print("Rotalumis executable not found. Please check the path.")
        return -1

# Save simulation results to a CSV
def save_results_to_csv(results, output_file):
    df = pd.DataFrame(results, columns=["Trace File", "Model File", "Makespan"])
    df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

# Visualize the results
def visualize_results(results):
    df = pd.DataFrame(results, columns=["Trace File", "Model File", "Makespan"])
    fig = px.bar(df, x="Model File", y="Makespan", color="Trace File", title="Makespan Comparison")
    fig.show()

if __name__ == "__main__":
    # Define paths to the trace.ini and POOSL model files
    trace_ini_path = os.path.expanduser("~/eclipse-workspace/xcps/models/trace.ini")
    model_file = os.path.expanduser("~/eclipse-workspace/xcps/models/xcps-model.poosl")

    # Run the simulation and collect results
    results = []
    makespan = run_performance_model(trace_ini_path, model_file)

    if makespan >= 0:
        results.append((trace_ini_path, model_file, makespan))
    else:
        print(f"Failed to run model: {model_file}")

    # Save results to a CSV
    output_csv = os.path.expanduser("~/eclipse-workspace/xcps/models/simulation_results.csv")
    save_results_to_csv(results, output_csv)

    # Visualize the results
    visualize_results(results)
