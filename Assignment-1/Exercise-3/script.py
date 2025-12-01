import subprocess
import re
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os
# --- Configuration ---
try:
    plt.style.use('seaborn-v0_8-whitegrid')
except:
    plt.style.use('ggplot')

# Array sizes to test
sizes = [10**5, 10**6,10**7]
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
        script_dir = os.path.dirname(os.path.abspath(__file__))
        exe_path = os.path.join(script_dir, "solution")
        res = subprocess.run([exe_path, str(size)], capture_output=True, text=True)
        if res.returncode == 0:
            t_init.append(float(init_re.search(res.stdout).group(1)))
            t_par_sol.append(float(parallel_re.search(res.stdout).group(1)))
            t_serial.append(float(serial_re.search(res.stdout).group(1)))

        # 2. Run Improved Solution
        exe_path = os.path.join(script_dir, "improved_solution")
        res2 = subprocess.run([exe_path, str(size)], capture_output=True, text=True)
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

# ==========================================
# GRAPH 5: Summary Table (Text & Image)
# ==========================================

# --- Part A: Print to Console ---
print("\n" + "="*75)
print(f"{'Size':<10} | {'Init (s)':<12} | {'Serial (s)':<12} | {'Par Orig (s)':<12} | {'Par Imp (s)':<12}")
print("-" * 75)
for i, size in enumerate(sizes):
    print(f"{format_xaxis(size,0):<10} | "
          f"{data['init'][i]:<12.5f} | "
          f"{data['serial'][i]:<12.5f} | "
          f"{data['parallel_sol'][i]:<12.5f} | "
          f"{data['parallel_imp'][i]:<12.5f}")
print("="*75 + "\n")

# --- Part B: Save as Image ---
fig, ax = plt.subplots(figsize=(10, len(sizes) * 0.5 + 2)) # Adjust height based on rows
ax.axis('tight')
ax.axis('off')

# Prepare table data
col_labels = ["Array Size", "Init Time", "Serial Time", "Par. Orig.", "Par. Imp."]
cell_text = []
for i, size in enumerate(sizes):
    row = [
        format_xaxis(size, 0),
        f"{data['init'][i]:.5f} s",
        f"{data['serial'][i]:.5f} s",
        f"{data['parallel_sol'][i]:.5f} s",
        f"{data['parallel_imp'][i]:.5f} s"
    ]
    cell_text.append(row)

# Create the table
table = ax.table(cellText=cell_text, colLabels=col_labels, loc='center', cellLoc='center')

# Styling
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1, 1.8) # Stretch height for readability

# Color headers to match your previous graphs
# 0=Size, 1=Init (Purple), 2=Serial (Gray), 3=Par Orig (Blue), 4=Par Imp (Green)
header_colors = ['#dddddd', '#D8BFD8', '#d3d3d3', '#add8e6', '#aaffaa'] 

for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_text_props(weight='bold')
        cell.set_facecolor(header_colors[col])

ax.set_title("5. Execution Time Summary Table", fontsize=14, fontweight='bold', y=0.95)

plt.tight_layout()
plt.savefig("execution_table.png", dpi=150, bbox_inches='tight')
plt.close()

# ==========================================
# GRAPH 6: Speedup Comparison Table
# ==========================================

# Calculate Speedups
speedup_orig_list = [s / p for s, p in zip(data["serial"], data["parallel_sol"])]
speedup_imp_list = [s / p for s, p in zip(data["serial"], data["parallel_imp"])]

# --- Part A: Print to Console ---
print("\n" + "="*50)
print(f"{'Size':<10} | {'Speedup Orig':<15} | {'Speedup Imp':<15}")
print("-" * 50)
for i, size in enumerate(sizes):
    print(f"{format_xaxis(size,0):<10} | "
          f"{speedup_orig_list[i]:<14.2f}x | "
          f"{speedup_imp_list[i]:<14.2f}x")
print("="*50 + "\n")

# --- Part B: Save as Image ---
fig, ax = plt.subplots(figsize=(8, len(sizes) * 0.5 + 2)) 
ax.axis('tight')
ax.axis('off')

# Prepare table data
col_labels = ["Array Size", "Original Speedup", "Improved Speedup"]
cell_text = []
for i, size in enumerate(sizes):
    row = [
        format_xaxis(size, 0),
        f"{speedup_orig_list[i]:.2f}x",
        f"{speedup_imp_list[i]:.2f}x"
    ]
    cell_text.append(row)

# Create the table
table = ax.table(cellText=cell_text, colLabels=col_labels, loc='center', cellLoc='center')

# Styling
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1, 1.8)

# Header Colors: Size (Gray), Orig (Blue), Imp (Green)
header_colors = ['#dddddd', '#add8e6', '#aaffaa']

for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_text_props(weight='bold')
        cell.set_facecolor(header_colors[col])
    else:
        # Highlight the "Improved" column values in bold green text for emphasis
        if col == 2:
            cell.set_text_props(weight='bold', color='darkgreen')

ax.set_title("6. Parallel Speedup Factor Table", fontsize=14, fontweight='bold', y=0.95)

plt.tight_layout()
plt.savefig("speedup_table.png", dpi=150, bbox_inches='tight')
plt.close()

print("\nVisualization Complete! Generated 6 files:")
print("1. execution_comparison.png")
print("2. speedup_analysis.png")
print("3. initialization_times.png")
print("4. overhead_analysis.png (Stacked Bar Chart)")
print("5. execution_table.png (New Summary Table)")
print("6. speedup_table.png")