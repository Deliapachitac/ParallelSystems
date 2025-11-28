import subprocess
import re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# --- Configuration ---
try:
    plt.style.use('seaborn-v0_8-whitegrid')
except:
    plt.style.use('ggplot')

# Array sizes to test
sizes = [10**5, 10**6]
num_runs = 5

# Regex patterns
init_re = re.compile(r"Initializing structs needed took: ([0-9.]+) seconds")
parallel_re = re.compile(r"Parallel execution for array size of .* took: ([0-9.]+) seconds")
serial_re = re.compile(r"Serial execution for array size of .* took: ([0-9.]+) seconds")

# --- Data Collection ---
data = {
    "sizes": sizes,
    "init": [],
    "serial": [],
    "parallel_sol": [],
    "parallel_imp": []
}

print(f"--- Starting Benchmark ({num_runs} runs per size) ---")

for size in sizes:
    print(f"Processing Array Size: {size:,}")
    
    t_init, t_serial, t_par_sol, t_par_imp = [], [], [], []

    for run in range(num_runs):
        # 1. Run Standard Solution
        res = subprocess.run(["./solution", str(size)], capture_output=True, text=True)
        if res.returncode == 0:
            t_init.append(float(init_re.search(res.stdout).group(1)))
            t_par_sol.append(float(parallel_re.search(res.stdout).group(1)))
            t_serial.append(float(serial_re.search(res.stdout).group(1)))

        # 2. Run Improved Solution
        res2 = subprocess.run(["./improved_solution", str(size)], capture_output=True, text=True)
        if res2.returncode == 0:
            t_par_imp.append(float(parallel_re.search(res2.stdout).group(1)))

    data["init"].append(np.mean(t_init))
    data["serial"].append(np.mean(t_serial))
    data["parallel_sol"].append(np.mean(t_par_sol))
    data["parallel_imp"].append(np.mean(t_par_imp))

# --- Helper: Format X Axis Labels ---
def format_xaxis(x, pos):
    if x >= 1e6: return f'{int(x/1e6)}M'
    if x >= 1e3: return f'{int(x/1e3)}k'
    return str(int(x))

# ==========================================
# GRAPH 1: Execution Time Comparison (Log)
# ==========================================
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(sizes, data["serial"], marker='x', ls='--', color='gray', label='Serial Baseline')
ax.plot(sizes, data["parallel_sol"], marker='o', color='tab:blue', label='Parallel (Original)')
ax.plot(sizes, data["parallel_imp"], marker='s', color='tab:green', label='Parallel (Improved)')

ax.set_title("1. Execution Time Comparison (Log Scale)", fontsize=14, fontweight='bold')
ax.set_xlabel("Array Size", fontsize=12)
ax.set_ylabel("Time (seconds)", fontsize=12)
ax.set_xscale('log')
ax.set_yscale('log')
ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_xaxis))
ax.set_xticks(sizes)
ax.legend()
plt.tight_layout()
plt.savefig("execution_comparison.png", dpi=150)
plt.close()

# ==========================================
# GRAPH 2: Speedup Analysis (Bar)
# ==========================================
speedup_sol = [s / p for s, p in zip(data["serial"], data["parallel_sol"])]
speedup_imp = [s / p for s, p in zip(data["serial"], data["parallel_imp"])]

fig, ax = plt.subplots(figsize=(10, 6))
width = 0.35
x = np.arange(len(sizes))

rects1 = ax.bar(x - width/2, speedup_sol, width, label='Original Speedup', color='skyblue')
rects2 = ax.bar(x + width/2, speedup_imp, width, label='Improved Speedup', color='seagreen')

ax.set_ylabel('Speedup Factor', fontsize=12)
ax.set_title('2. Parallel Speedup (Higher is Better)', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels([format_xaxis(s, 0) for s in sizes])
ax.legend()
plt.tight_layout()
plt.savefig("speedup_analysis.png", dpi=150)
plt.close()

# ==========================================
# GRAPH 3: Initialization Times Only
# ==========================================
fig, ax = plt.subplots(figsize=(10, 6))

ax.plot(sizes, data["init"], marker='D', linestyle='-', color='purple', linewidth=2, label='Init Time')

ax.set_title("3. Initialization Cost Scaling", fontsize=14, fontweight='bold')
ax.set_xlabel("Array Size", fontsize=12)
ax.set_ylabel("Initialization Time (seconds)", fontsize=12)
ax.set_xscale('log')
ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_xaxis))
ax.set_xticks(sizes)
ax.grid(True, which="both", ls="--", alpha=0.5)

# Annotate points
for i, size in enumerate(sizes):
    ax.annotate(f"{data['init'][i]:.5f}s", 
                (size, data['init'][i]), textcoords="offset points", xytext=(0,10), ha='center', color='purple', fontweight='bold')

plt.tight_layout()
plt.savefig("initialization_times.png", dpi=150)
plt.close()

# ==========================================
# GRAPH 4: Init vs Execution (Stacked Bar)
# ==========================================
fig, ax = plt.subplots(figsize=(10, 6))

x = np.arange(len(sizes))
width = 0.5

# We use the 'Improved' parallel time for comparison as it's the target performance
p1 = ax.bar(x, data["init"], width, label='Initialization', color='purple', alpha=0.7)
p2 = ax.bar(x, data["parallel_imp"], width, bottom=data["init"], label='Execution (Improved)', color='tab:green', alpha=0.7)

ax.set_title("4. Total Runtime Breakdown (Init vs Exec)", fontsize=14, fontweight='bold')
ax.set_ylabel("Total Time (seconds)", fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels([format_xaxis(s, 0) for s in sizes])
ax.legend()

# Annotate the percentage of time spent on Initialization
for i in range(len(sizes)):
    total = data["init"][i] + data["parallel_imp"][i]
    init_pct = (data["init"][i] / total) * 100
    
    # Place text above the bar
    ax.text(i, total, f"Init is {init_pct:.1f}% of total", ha='center', va='bottom', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig("overhead_analysis.png", dpi=150)
plt.close()

print("\nVisualization Complete! Generated 4 files:")
print("1. execution_comparison.png")
print("2. speedup_analysis.png")
print("3. initialization_times.png")
print("4. overhead_analysis.png (Stacked Bar Chart)")