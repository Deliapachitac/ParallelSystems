import subprocess 
import matplotlib.pyplot as plt 
import re 
import numpy as np 
import os
# Degrees of polynomials and number of threads to test 
polyonomial_degrees = [ 10**2,10**3, 10**4, 10**5 ] 
thread_num =[2,4 ,8] 


# Array to store times 
initialization_time = [] 
serial_time = [] 
parallel_time = [] 

# Regex patterns to capture times from output 
init_re = re.compile(r"Initialization time: ([0-9.]+) seconds") 
serial_re = re.compile(r"Serial multiplication time: ([0-9.]+) seconds") 
parallel_re = re.compile(r"Parallel multiplication time: ([0-9.]+) seconds") 
num_runs = 1

# Results dictionary: method -> {(threads, degree): avg_time}
results = {"Initialization": {}, "Serial": {}, "Parallel": {}}

for degree in  polyonomial_degrees: 
    print(f"Running for polynomial degree: {degree}") 
    for threads in thread_num : 
        print(f" Using {threads} threads") 

        # Temporary lists to store times for averaging 
        run_temp_init = [] 
        run_temp_serial = [] 
        run_temp_parallel = [] 

        for run in range(num_runs): 
            print(f" Run {run + 1}/{num_runs}") 

            script_dir = os.path.dirname(os.path.abspath(__file__))
            exe_path = os.path.join(script_dir, "solution1")
           
            result = subprocess.run([exe_path, str(degree), str(threads)],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)
            output = result.stdout 

            # Extract times using regex 
            run_temp_init.append(float(init_re.search(output).group(1))) 
            run_temp_serial.append(float(serial_re.search(output).group(1))) 
            run_temp_parallel.append(float(parallel_re.search(output).group(1)))

        results["Initialization"][(threads, degree)] = sum(run_temp_init) / num_runs
        results["Serial"][(threads, degree)] = sum(run_temp_serial) / num_runs      
        results["Parallel"][(threads, degree)] = sum(run_temp_parallel) / num_runs


# Plotting the results
labels = [f"T{t}/D{d}" for t in thread_num for d in polyonomial_degrees]
x = np.arange(len(labels))
width = 0.35

# Plot 1 Serial vs Parallel   
fig1, ax1 = plt.subplots(figsize=(14,6))

for idx, method in enumerate(["Serial", "Parallel"]):
    y_values = [results[method][(t,d)] for t in thread_num for d in polyonomial_degrees]
    ax1.bar(x + idx*width, y_values, width, label=method)

ax1.set_xlabel("Threads-Degree")
ax1.set_ylabel("Average Time (seconds)")
ax1.set_title("Polynomial Multiplication: Serial vs Parallel")
ax1.set_xticks(x + width/2)
ax1.set_xticklabels(labels, rotation=45)
ax1.legend()

plt.tight_layout()
plt.savefig("poly_times_serial_parallel.png", dpi=300)
plt.show()

# Plot 2 Initialization 
fig2, ax2 = plt.subplots(figsize=(14,6))

y_init = [results["Initialization"][(t,d)] for t in thread_num for d in polyonomial_degrees]
ax2.bar(x, y_init, width, color="orange", label="Initialization")

ax2.set_xlabel("Threads-Degree")
ax2.set_ylabel("Average Time (seconds)")
ax2.set_title("Polynomial Multiplication: Initialization Time")
ax2.set_xticks(x)
ax2.set_xticklabels(labels, rotation=45)
ax2.legend()

plt.tight_layout()
plt.savefig("poly_times_initialization.png", dpi=300)
plt.show()

# Save times to an array 
table_data = []
for t in thread_num:
    for d in polyonomial_degrees:
        serial_val = results['Serial'][(t,d)]
        parallel_val = results['Parallel'][(t,d)]
        improvement = serial_val / parallel_val if parallel_val > 0 else 0.0

        table_data.append([
            f"T{t}/D{d}",
            f"{serial_val:.6f}",
            f"{parallel_val:.6f}",
            f"{improvement:.2f}x"
        ])

col_labels = ["Threads-Degree", "Serial", "Parallel", "Improvement (Serial/Parallel)"]

fig3, ax3 = plt.subplots(figsize=(12,4))
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
