import subprocess
import re
import matplotlib.pyplot as plt
import numpy as np

# Array sizes to test
sizes = [10**5, 10**6, 10**7, 10**8]

# Store times
init_times = []
parallel_times_solution = []
serial_times_solution = []
parallel_times_improved = []

# Regex to capture times
init_re = re.compile(r"Initializing structs needed took: ([0-9.]+) seconds")
parallel_re = re.compile(r"Parallel execution for array size of .* took: ([0-9.]+) seconds")
serial_re = re.compile(r"Serial execution for array size of .* took: ([0-9.]+) seconds")

num_runs = 5

for size in sizes:
    print(f"Running for array size: {size}")

    # Temporary lists for averaging
    temp_init = []
    temp_parallel_solution = []
    temp_serial_solution = []
    temp_parallel_improved = []

    for run in range(num_runs):
        print(f"  Run {run+1}/{num_runs} (solution)")
        result = subprocess.run(["./solution", str(size)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)
        output = result.stdout
        if run == 0:  # only count initialization once
            temp_init.append(float(init_re.search(output).group(1)))
        temp_parallel_solution.append(float(parallel_re.search(output).group(1)))
        temp_serial_solution.append(float(serial_re.search(output).group(1)))

        print(f"  Run {run+1}/{num_runs} (improved_solution)")
        result2 = subprocess.run(["./improved_solution", str(size)],
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 text=True)
        output2 = result2.stdout
        if run == 0:  # only count initialization once
            temp_init.append(float(init_re.search(output2).group(1)))
        temp_parallel_improved.append(float(parallel_re.search(output2).group(1)))

    # Compute averages
    init_times.append(np.mean(temp_init))
    parallel_times_solution.append(np.mean(temp_parallel_solution))
    serial_times_solution.append(np.mean(temp_serial_solution))
    parallel_times_improved.append(np.mean(temp_parallel_improved))

# -----------------------
# Plot initialization times
plt.figure(figsize=(10,5))
plt.plot(sizes, init_times, marker='d', color='purple', label='Initialization')
plt.xlabel('Array Size (log scale)')
plt.ylabel('Time (seconds)')
plt.title('Array Initialization Time (Average of 5 runs)')
plt.xscale('log')
plt.xticks(sizes, ['1e5','1e6','1e7','1e8'])
plt.grid(True, ls="--")
plt.legend()
plt.tight_layout()
plt.savefig("initialization_times.png")
plt.close()

# -----------------------
# Plot execution times
plt.figure(figsize=(10,5))
plt.plot(sizes, serial_times_solution, marker='x', label='Serial (solution)')
plt.plot(sizes, parallel_times_solution, marker='o', label='Parallel (solution)')
plt.plot(sizes, parallel_times_improved, marker='s', label='Parallel (improved_solution)')
plt.xlabel('Array Size (log scale)')
plt.ylabel('Time (seconds)')
plt.title('Execution Times (Average of 5 runs)')
plt.xscale('log')
plt.xticks(sizes, ['1e5','1e6','1e7','1e8'])
plt.grid(True, ls="--")
plt.legend()
plt.tight_layout()
plt.savefig("execution_times.png")
plt.close()

print("Graphs saved as 'initialization_times.png' and 'execution_times.png'")
