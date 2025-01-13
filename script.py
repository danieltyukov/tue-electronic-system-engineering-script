import subprocess
import os

# Adjust the path to point to your local rotalumis executable
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
            print(f"Error: {proc.stderr}")
            return -1
    except FileNotFoundError:
        print("Rotalumis executable not found. Please check the path.")
        return -1

if __name__ == "__main__":
    # Define paths to the trace.ini and POOSL model file
    trace_ini_path = os.path.expanduser("~/eclipse-workspace/xcps/models/trace.ini")
    model_path = os.path.expanduser("~/eclipse-workspace/xcps/models/xcps-model.poosl")

    # Run the performance model
    makespan = run_performance_model(trace_ini_path, model_path)

    # Print the results
    if makespan >= 0:
        print(f"Batch Makespan: {makespan}")
    else:
        print("Failed to run the performance model.")
