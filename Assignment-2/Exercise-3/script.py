import subprocess 
import matplotlib.pyplot as plt 
import re 
import numpy as np 
import os

# Array sizes and number of threads to test (Based on exercise requirements)
array_sizes = [10**3 ,10**4, 10**5, 10**6] 
thread_num = [2, 4, 8] 

num_runs = 3 

# Regex patterns to capture times from output 
serial_re = re.compile(r"Serial mergesort time: ([0-9.]+) seconds") 
parallel_re = re.compile(r"Parallel mergesort time: ([0-9.]+) seconds") 

# Results dictionaries
serial_results = {}   # size -> avg_time
parallel_results = {} # (size, threads) -> avg_time

script_dir = os.path.dirname(os.path.abspath(__file__))
exe_path = os.path.join(script_dir, "exercise_3") 

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

    # Run Parallel Mode for different thread counts
    for threads in thread_num: 
        print(f"  Running Parallel ({threads} threads)", end=" ", flush=True) 
        temp_parallel = []
        for run in range(num_runs):
            print(f" Run {run + 1}/{num_runs}")  
            result = subprocess.run([exe_path, str(size), "p", str(threads)],
                                    stdout=subprocess.PIPE, text=True)
            output = result.stdout
            temp_parallel.append(float(parallel_re.search(output).group(1)))

        parallel_results[(size, threads)] = sum(temp_parallel) / num_runs
        


# Plotting the results
labels = [f"T{t}/S{size}" for size in array_sizes for t in thread_num]
x = np.arange(len(labels))
width = 0.35

fig1, ax1 = plt.subplots(figsize=(14, 7))

y_serial = []
y_parallel = []
for size in array_sizes:
    for t in thread_num:
        y_serial.append(serial_results[size])
        y_parallel.append(parallel_results[(size, t)])

ax1.bar(x - width/2, y_serial, width, label='Serial', color="#af215c")
ax1.bar(x + width/2, y_parallel, width, label='Parallel', color="#51dfdf")

ax1.set_xlabel("Threads / Array Size")
ax1.set_ylabel("Execution Time (seconds)")
ax1.set_title("Merge Sort Performance: Serial vs Parallel")
ax1.set_xticks(x)
ax1.set_xticklabels(labels, rotation=45)
ax1.legend()
ax1.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig("mergesort_bars.png", dpi=300)
plt.show()

#Table summary
table_data = []
for size in array_sizes:
    for t in thread_num:
        s_val = serial_results[size]
        p_val = parallel_results[(size, t)]
        speedup = s_val / p_val
        table_data.append([size, t, f"{s_val:.4f}", f"{p_val:.4f}", f"{speedup:.2f}x"])

col_labels = ["Array Size", "Threads", "Serial Time (s)", "Parallel Time (s)", "Speedup"]

fig2, ax2 = plt.subplots(figsize=(12, 5))
ax2.axis('tight')
ax2.axis('off')

summary_table = ax2.table(cellText=table_data, colLabels=col_labels, loc='center', cellLoc='center')
summary_table.auto_set_font_size(False)
summary_table.set_fontsize(10)
summary_table.scale(1.2, 1.5)


for (row, col), cell in summary_table.get_celld().items():
    if row == 0:
        cell.set_facecolor("#444444")
        cell.set_text_props(weight='bold', color='white')

plt.title("Merge Sort Execution Summary & Speedup", pad=20)
plt.savefig("mergesort_summary_table.png", dpi=300)
plt.show()