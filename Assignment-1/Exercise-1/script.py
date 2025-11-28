import subprocess
import matplotlib.pyplot as plt
import re
import numpy as np

# Degrees of polynomials and number of threads to test 
polyonomial_degrees = [ 10**3, 10**4]
thread_num =[2,4 ,8]

# Storage structures
parallel_times = {t: [] for t in thread_num}   # parallel times for each thread count
serial_time = []                                # serial time is same regardless of thread count
init_time = []                                   # optional if you need it

# Regex patterns
init_re = re.compile(r"Initialization time: ([0-9.]+) seconds")
serial_re = re.compile(r"Serial multiplication time: ([0-9.]+) seconds")
parallel_re = re.compile(r"Parallel multiplication time: ([0-9.]+) seconds")

num_runs = 5

# Results dictionary: method -> {(threads, degree): avg_time}
results = {"Initialization": {}, "Serial": {}, "Parallel": {}}

for  degree in polyonomial_degrees:
    print(f"Running for polynomial degree: {degree}")
    

    for threads in thread_num :
        print(f"  Using {threads} threads")

        run_temp_parallel = []

        for run in range(num_runs):
            result = subprocess.run(["./exercise_1", str(degree), str(threads)],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)
            output = result.stdout

            run_temp_parallel.append(float(parallel_re.search(output).group(1)))

        # Compute average times
        avg_init_time = sum(run_temp_init) / num_runs
        avg_serial_time = sum(run_temp_serial) / num_runs
        avg_parallel_time = sum(run_temp_parallel) / num_runs

        # Store average times in results dictionary
        results["Initialization"][(threads, degree)] = avg_init_time
        results["Serial"][(threads, degree)] = avg_serial_time
        results["Parallel"][(threads, degree)] = avg_parallel_time

        


labels = [f"T{t}/D{d}" for t in thread_num for d in polyonomial_degrees]
x = np.arange(len(labels))
width = 0.25

fig, ax = plt.subplots(figsize=(14,6))

for idx, method in enumerate(["Initialization", "Serial", "Parallel"]):
    y_values = [results[method][(t,d)] for t in thread_num for d in polyonomial_degrees]
    ax.bar(x + idx*width, y_values, width, label=method)

ax.set_xlabel("Threads-Degree")
ax.set_ylabel("Average Time (seconds)")
ax.set_title("Polynomial Multiplication Benchmark")
ax.set_xticks(x + width)
ax.set_xticklabels(labels, rotation=45)
ax.legend()

plt.tight_layout()
plt.savefig("poly_times.png", dpi=300)
plt.show()
