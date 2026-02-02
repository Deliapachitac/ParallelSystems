import subprocess
import matplotlib.pyplot as plt
import re
import numpy as np
import os

# Degrees of polynomials to test
polynomial_degrees = [10**2, 10**3, 10**4, 10**5]

# Regex patterns to capture times from output
init_re = re.compile(r"Initialization time: ([0-9.]+) seconds")
serial_re = re.compile(r"Serial multiplication time: ([0-9.]+) seconds")
simd_re = re.compile(r"SIMD multiplication time: ([0-9.]+) seconds")

num_runs = 2

# Results dictionary: method -> {degree: avg_time}
results = {"Initialization": {}, "Serial": {}, "SIMD": {}}

for degree in polynomial_degrees:
	print(f"Running for polynomial degree: {degree}")

	run_temp_init = []
	run_temp_serial = []
	run_temp_simd = []

	for run in range(num_runs):
		print(f" Run {run + 1}/{num_runs}")

		script_dir = os.path.dirname(os.path.abspath(__file__))
		exe_path = os.path.join(script_dir, "solution")

		result = subprocess.run([exe_path, str(degree)],
								stdout=subprocess.PIPE,
								stderr=subprocess.PIPE,
								text=True)
		output = result.stdout

		run_temp_init.append(float(init_re.search(output).group(1)))
		run_temp_serial.append(float(serial_re.search(output).group(1)))
		run_temp_simd.append(float(simd_re.search(output).group(1)))

	results["Initialization"][degree] = sum(run_temp_init) / num_runs
	results["Serial"][degree] = sum(run_temp_serial) / num_runs
	results["SIMD"][degree] = sum(run_temp_simd) / num_runs

# Plot 1: Serial vs SIMD
labels = [f"D{d}" for d in polynomial_degrees]
x = np.arange(len(labels))
width = 0.35

fig1, ax1 = plt.subplots(figsize=(12, 6))

serial_vals = [results["Serial"][d] for d in polynomial_degrees]
simd_vals = [results["SIMD"][d] for d in polynomial_degrees]

ax1.bar(x - width/2, serial_vals, width, label="Serial")
ax1.bar(x + width/2, simd_vals, width, label="SIMD")

ax1.set_xlabel("Polynomial Degree")
ax1.set_ylabel("Average Time (seconds)")
ax1.set_title("Polynomial Multiplication: Serial vs SIMD")
ax1.set_xticks(x)
ax1.set_xticklabels(labels)
ax1.legend()

plt.tight_layout()
plt.savefig("poly_times_serial_simd.png", dpi=300)
plt.show()

# Plot 2: Initialization time
fig2, ax2 = plt.subplots(figsize=(12, 6))

init_vals = [results["Initialization"][d] for d in polynomial_degrees]
ax2.bar(x, init_vals, width, color="orange", label="Initialization")

ax2.set_xlabel("Polynomial Degree")
ax2.set_ylabel("Average Time (seconds)")
ax2.set_title("Polynomial Multiplication: Initialization Time")
ax2.set_xticks(x)
ax2.set_xticklabels(labels)
ax2.legend()

plt.tight_layout()
plt.savefig("poly_times_initialization.png", dpi=300)
plt.show()

# Table summary
table_data = []
for d in polynomial_degrees:
	serial_val = results["Serial"][d]
	simd_val = results["SIMD"][d]
	improvement = serial_val / simd_val if simd_val > 0 else 0.0

	table_data.append([
		f"D{d}",
		f"{serial_val:.6f}",
		f"{simd_val:.6f}",
		f"{improvement:.2f}x"
	])

col_labels = ["Degree", "Serial", "SIMD", "Improvement (Serial/SIMD)"]

fig3, ax3 = plt.subplots(figsize=(10, 4))
ax3.axis('tight')
ax3.axis('off')

table = ax3.table(cellText=table_data,
				  colLabels=col_labels,
				  loc='center')

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)

for (row, col), cell in table.get_celld().items():
	if row == 0:
		cell.set_facecolor("#ccccff")
		cell.set_text_props(weight='bold', color='black')

plt.title("Summary of Average Times and Speedup")
plt.savefig("poly_times_table.png", dpi=300)
plt.show()
