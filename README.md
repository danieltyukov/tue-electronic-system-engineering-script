# Electronic Systems Engineering: Design-Space Exploration Scripts

Python and C scripts that drive and evaluate the xCPS production line model for the TU/e
design-based-learning project in Electronic Systems Engineering (course 5XIC0). This
repository holds the scripting part of the project. The system itself is modelled in POOSL
and in SysML, kept in the sibling repositories linked below.

The design question was which combination of component speeds to build. Belts, the index
table and the two gantry arms can each be ordered in a slow, normal or fast variant. Faster
parts cost more but reduce the time to produce a batch (the makespan), which raises the
number of units that can be sold. The scripts here run the performance model over the full
set of speed combinations and turn each makespan into an estimated profit, so the design
space can be compared on a single makespan-versus-profit plot instead of by hand.

## What the scripts do

`script.py` is the exploration driver. For each speed combination it:

1. Rewrites the speed presets in the POOSL model file (`addSlowBelts` / `addNormalBelts` /
   `addFastBelts`, and the matching index and arm presets).
2. Runs the model on the Rotalumis simulation engine and reads the makespan the model
   prints at the end of the run.
3. Converts that makespan into a profit using a cost-and-volume model: a bill-of-materials
   cost per component variant, a sales price derived from it, a sales volume that grows as
   makespan drops, and a delay penalty for engineering changes.
4. Collects every result into a table, writes it to CSV, and draws an interactive
   makespan-versus-profit scatter plot with Plotly.

`profit.c` is a standalone C version of the same profit calculation for a single
configuration passed on the command line. It made it possible to check the financial model
on its own, separately from the simulation loop.

## Contents

| File | Role |
| --- | --- |
| `script.py` | Design-space exploration driver. Sweeps the belt, index, gantry-1 and gantry-2 speed combinations, runs the POOSL model through Rotalumis for each, computes profit, writes `design_space_results.csv` and shows the makespan-versus-profit plot. |
| `profit.c` | Command-line C implementation of the profit model for one configuration (makespan and the four component variants as arguments). Prints delay, price, volume, cost and profit. |
| `design_space_results.csv` | Recorded results of an exploration run: belt, index and gantry speeds with the resulting makespan and profit for each configuration. |
| `old/scriptv1.py` … `old/scriptv7.py` | Earlier iterations of the driver, kept to show how the script grew from a first pass to the current version. |
| `trace.etf` | Execution trace from a single simulation run, in the TRACE format. |
| `trace.view` | Saved view settings for inspecting that trace. |
| `.vscode/tasks.json` | VS Code build task that compiles `profit.c` with gcc. |

## Running

`script.py` expects a working xCPS POOSL model and the Rotalumis executable. The paths to
the Rotalumis binary, the trace configuration and the model file are set at the top of the
script and point at a local Eclipse workspace, so adjust them to match your setup. The
script also needs `pandas` and `plotly`:

```
pip install pandas plotly
python script.py
```

It writes `design_space_results.csv` and opens the makespan-versus-profit plot in a browser.

`profit.c` compiles with gcc and takes the makespan and the four component variants as
arguments:

```
gcc profit.c -o profit
./profit <makespan> <belt> <index> <arm1> <arm2> <adjustments>
```

where each component variant is `s`, `n` or `f`.

## Related repositories

This is one part of the Electronic Systems Engineering design-based-learning project. The
other parts:

- [tue-electronic-system-engineering-poosl](https://github.com/danieltyukov/tue-electronic-system-engineering-poosl): POOSL performance model these scripts drive.
- [tue-electronic-system-engineering-sysml](https://github.com/danieltyukov/tue-electronic-system-engineering-sysml): SysML model of the same system.

## Technologies

- Python with pandas and Plotly
- POOSL model run on the Rotalumis simulation engine
- C compiled with gcc
