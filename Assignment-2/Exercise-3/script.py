import subprocess 
import matplotlib.pyplot as plt 
import re 
import numpy as np 
import os

# Array sizes and number of threads to test (Based on exercise requirements)
array_sizes = [10**3 ,10**4, 10**5, 10**6] 
thread_num = [2, 4, 8] 

num_runs = 4

# Regex patterns to capture times from output 
serial_re = re.compile(r"Serial mergesort time: ([0-9.]+) seconds") 
parallel_re = re.compile(r"Parallel mergesort time: ([0-9.]+) seconds") 
optimal_re = re.compile(r"Parallel mergesort optimal time: ([0-9.]+) seconds")

# Results dictionaries
serial_results = {}   # size -> avg_time
parallel_results = {} # (size, threads) -> avg_time
optimal_results = {} # (size, threads) ->avg_time

script_dir = os.path.dirname(os.path.abspath(__file__))
exe_path = os.path.join(script_dir, "solution3") 

for size in array_sizes: 
    print(f"\n--- Testing Array Size: {size} ---") 
    
    #Run Serial Mode (Once per size, threads don't matter)
    temp_serial = []
    print(f"Running Serial Mode", end=" ", flush=True)
    for run in range(num_runs):
        print(f" Run {run + 1}/{num_runs}") 

        result = subprocess.run([exe_path, str(size), "s", "1"], 
                                stdout=subprocess.PIPE, text=True)
        output = result.stdout
        temp_serial.append(float(serial_re.search(output).group(1)))

    
    serial_results[size] = sum(temp_serial) / num_runs

    # Run Parallel Mode and Optimal Parallel Mode for different thread counts
    for threads in thread_num: 
        print(f"Running Parallel ({threads} threads)\n", end=" ", flush=True) 
        temp_parallel = []
        temp_optimal = []
        for run in range(num_runs):
            print(f" Run {run + 1}/{num_runs}")  
            result = subprocess.run([exe_path, str(size), "p", str(threads)],
                                    stdout=subprocess.PIPE, text=True)
            output = result.stdout
            temp_parallel.append(float(parallel_re.search(output).group(1)))
            temp_optimal.append(float(optimal_re.search(output).group(1)))

        parallel_results[(size, threads)] = sum(temp_parallel) / num_runs
        optimal_results[(size, threads)] = sum(temp_optimal) / num_runs
        


# Plotting all the results
labels = [f"T{t}/S{size}" for size in array_sizes for t in thread_num]
x = np.arange(len(labels))
width = 0.25

fig1, ax1 = plt.subplots(figsize=(15, 8))

y_serial = []
y_parallel = []
y_optimal = []
for size in array_sizes:
    for t in thread_num:
        y_serial.append(serial_results[size])
        y_parallel.append(parallel_results[(size, t)])
        y_optimal.append(optimal_results[(size, t)])

ax1.bar(x - width, y_serial, width, label='Serial', color="#af215c")
ax1.bar(x, y_parallel, width, label='Parallel Basic', color="#51dfdf")
ax1.bar(x + width, y_optimal, width, label='Parallel Optimal', color="#f39c12")

ax1.set_xlabel("Threads / Array Size")
ax1.set_ylabel("Execution Time (seconds)")
ax1.set_title("Merge Sort Comparison: Serial vs Parallel vs Optimal")
ax1.set_xticks(x)
ax1.set_xticklabels(labels, rotation=45)
ax1.legend()
ax1.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig("mergesort_comparison_bars.png", dpi=100)
plt.close(fig1)

#TABLE 1: BASIC PARALLEL SPEEDUP 
table1_data = []
for size in array_sizes:
    for t in thread_num:
        s_val = serial_results[size]
        p_val = parallel_results[(size, t)]
        speedup = s_val / p_val if p_val > 0 else 0
        table1_data.append([size, t, f"{s_val:.4f}", f"{p_val:.4f}", f"{speedup:.2f}x"])

fig_t1, ax_t1 = plt.subplots(figsize=(10, 6))
ax_t1.axis('tight'); ax_t1.axis('off')
tab1 = ax_t1.table(cellText=table1_data, colLabels=["Size", "Threads", "Serial (s)", "Parallel (s)", "Speedup"], loc='center', cellLoc='center')
tab1.auto_set_font_size(False); tab1.set_fontsize(10); tab1.scale(1.2, 2)
for (row, col), cell in tab1.get_celld().items():
    if row == 0: cell.set_facecolor("#51dfdf")
plt.title("Table 1: Basic Parallel Mergesort Speedup", pad=20)
plt.savefig("table_basic_parallel.png", dpi=100)
plt.close(fig_t1)

#TABLE 2: OPTIMAL PARALLEL SPEEDUP
table2_data = []
for size in array_sizes:
    for t in thread_num:
        s_val = serial_results[size]
        o_val = optimal_results[(size, t)]
        speedup = s_val / o_val if o_val > 0 else 0
        table2_data.append([size, t, f"{s_val:.4f}", f"{o_val:.4f}", f"{speedup:.2f}x"])

fig_t2, ax_t2 = plt.subplots(figsize=(10, 6))
ax_t2.axis('tight'); ax_t2.axis('off')
tab2 = ax_t2.table(cellText=table2_data, colLabels=["Size", "Threads", "Serial (s)", "Optimal (s)", "Speedup"], loc='center', cellLoc='center')
tab2.auto_set_font_size(False); tab2.set_fontsize(10); tab2.scale(1.2, 2)
for (row, col), cell in tab2.get_celld().items():
    if row == 0: cell.set_facecolor("#f39c12")
plt.title("Table 2: Optimal Parallel Mergesort Speedup (Cutoff=1000)", pad=20)
plt.savefig("table_optimal_parallel.png", dpi=100)
plt.close(fig_t2)


#GRAPH: SERIAL vs PARALLEL vs OPTIMAL (Fixed Threads = 4)
fig3, ax3 = plt.subplots(figsize=(10, 6))


y_s = [serial_results[s] for s in array_sizes]
y_p = [parallel_results[(s, 4)] for s in array_sizes]
y_o = [optimal_results[(s, 4)] for s in array_sizes]


ax3.plot(array_sizes, y_s, label='Serial', marker='o', color="#af215c", linewidth=2)
ax3.plot(array_sizes, y_p, label='Basic Parallel (T=4)', marker='s', color="#51dfdf", linewidth=2)
ax3.plot(array_sizes, y_o, label='Optimal Parallel (T=4)', marker='^', color="#f39c12", linewidth=2)

ax3.set_xscale('log')
ax3.set_xlabel("Array Size (Log Scale)")
ax3.set_ylabel("Execution Time (seconds)")
ax3.set_title("Performance Trend Analysis (4 Threads)")
ax3.legend()
ax3.grid(True, which="both", linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig("comparison_threads_4.png", dpi=100)
plt.close(fig3)

# Graph: SERIAL vs PARALLEL vs OPTIMAL (Fixed Size = 10**6 )
fig4, ax4 = plt.subplots(figsize=(10, 6))

fixed_size = 10**6
y_p_scaling = [parallel_results[(fixed_size, t)] for t in thread_num]
y_o_scaling = [optimal_results[(fixed_size, t)] for t in thread_num]
y_s_line = [serial_results[fixed_size]] * len(thread_num)

ax4.plot(thread_num, y_s_line, 'r--', label='Serial Baseline', linewidth=2)
ax4.plot(thread_num, y_p_scaling, marker='s', label='Basic Parallel', color="#51dfdf", linewidth=2)
ax4.plot(thread_num, y_o_scaling, marker='o', label='Optimal Parallel', color="#f39c12", linewidth=2)

ax4.set_xlabel("Number of Threads")
ax4.set_ylabel("Execution Time (seconds)")
ax4.set_title(f"Scaling Analysis for Array Size $10^6$")
ax4.set_xticks(thread_num)
ax4.legend()
ax4.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig("comparison_size_10_6.png", dpi=100)
plt.close(fig4)