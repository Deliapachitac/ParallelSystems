import subprocess
import matplotlib.pyplot as plt
import re
import numpy as np
import os

# Polynomial degrees and MPI process counts to test
polynomial_degrees = [10**2, 10**3, 10**4]
process_counts = [2, 4]

# Regex patterns to capture MPI timing output
send_re  = re.compile(r"Sending data time:\s*([0-9.]+)")
comp_re  = re.compile(r"Parallel computation time:\s*([0-9.]+)")
recv_re  = re.compile(r"Receiving data time:\s*([0-9.]+)")
total_re = re.compile(r"Total multiplication time:\s*([0-9.]+)")


num_runs = 4

# Results dictionary: category -> {(processes, degree): avg_time}
results = {
    "Send": {},
    "Compute": {},
    "Receive": {},
    "Total": {}
}

for degree in polynomial_degrees:
    print(f"\nRunning for polynomial degree: {degree}")

    for procs in process_counts:
        print(f"  Using {procs} MPI processes")

        # Temporary lists for averaging
        send_times = []
        comp_times = []
        recv_times = []
        total_times = []

        for run in range(num_runs):
            print(f"    Run {run + 1}/{num_runs}")

            script_dir = os.path.dirname(os.path.abspath(__file__))
            exe_path = os.path.join(script_dir, "solution")

            # Run MPI program
            result = subprocess.run(
                ["mpirun", "-np", str(procs), exe_path, str(degree)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            output = result.stdout

            # Extract times
            send_times.append(float(send_re.search(output).group(1)))
            comp_times.append(float(comp_re.search(output).group(1)))
            recv_times.append(float(recv_re.search(output).group(1)))
            total_times.append(float(total_re.search(output).group(1)))

        # Store averages
        results["Send"][(procs, degree)] = sum(send_times) / num_runs
        results["Compute"][(procs, degree)] = sum(comp_times) / num_runs
        results["Receive"][(procs, degree)] = sum(recv_times) / num_runs
        results["Total"][(procs, degree)] = sum(total_times) / num_runs


# -----------------------------
# Plotting
# -----------------------------

labels = [f"P{p}/D{d}" for p in process_counts for d in polynomial_degrees]
x = np.arange(len(labels))
width = 0.2

# Plot 1: Send, Compute, Receive, Total
fig1, ax1 = plt.subplots(figsize=(16, 6))

for idx, method in enumerate(["Send", "Compute", "Receive", "Total"]):
    y_values = [results[method][(p, d)] for p in process_counts for d in polynomial_degrees]
    ax1.bar(x + idx*width, y_values, width, label=method)

ax1.set_xlabel("Processes - Degree")
ax1.set_ylabel("Average Time (seconds)")
ax1.set_title("MPI Polynomial Multiplication Timings")
ax1.set_xticks(x + width*1.5)
ax1.set_xticklabels(labels, rotation=45)
ax1.legend()

plt.tight_layout()
plt.savefig("mpi_poly_times.png", dpi=300)
plt.show()

# -----------------------------
# Summary Table
# -----------------------------

table_data = []
for p in process_counts:
    for d in polynomial_degrees:
        table_data.append([
            f"P{p}/D{d}",
            f"{results['Send'][(p,d)]:.6f}",
            f"{results['Compute'][(p,d)]:.6f}",
            f"{results['Receive'][(p,d)]:.6f}",
            f"{results['Total'][(p,d)]:.6f}"
        ])

col_labels = ["Proc-Degree", "Send", "Compute", "Receive", "Total"]

fig2, ax2 = plt.subplots(figsize=(14, 5))
ax2.axis('tight')
ax2.axis('off')

table = ax2.table(
    cellText=table_data,
    colLabels=col_labels,
    loc='center'
)

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)

for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_facecolor("#ccccff")
        cell.set_text_props(weight='bold')

plt.title("MPI Timing Summary")
plt.savefig("mpi_poly_times_table.png", dpi=300)
plt.show()
