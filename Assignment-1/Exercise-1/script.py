import subprocess
import matplotlib.pyplot as plt
import re

# Degrees and thread counts
polyonomial_degrees = [10**3, 10**4]
thread_num =[2,4, 8, 16]

# Storage structures
parallel_times = {t: [] for t in thread_num}   # parallel times for each thread count
serial_time = []                                # serial time is same regardless of thread count
init_time = []                                   # optional if you need it

# Regex patterns
init_re = re.compile(r"Initialization time: ([0-9.]+) seconds")
serial_re = re.compile(r"Serial multiplication time: ([0-9.]+) seconds")
parallel_re = re.compile(r"Parallel multiplication time: ([0-9.]+) seconds")

num_runs = 5

for degree in polyonomial_degrees:
    print(f"Running for polynomial degree: {degree}")

    # serial and init times are same regardless of thread count → measure once (e.g., using 1 thread)
    run_temp_init = []
    run_temp_serial = []

    for run in range(num_runs):
        result = subprocess.run(["./exercise_1", str(degree), "1"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout
        run_temp_init.append(float(init_re.search(output).group(1)))
        run_temp_serial.append(float(serial_re.search(output).group(1)))

    init_time.append(sum(run_temp_init) / num_runs)
    serial_time.append(sum(run_temp_serial) / num_runs)

    # Now measure parallel times for 4/8/16 threads
    for threads in thread_num:
        print(f"  Using {threads} threads")

        run_temp_parallel = []

        for run in range(num_runs):
            result = subprocess.run(["./exercise_1", str(degree), str(threads)],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)
            output = result.stdout

            run_temp_parallel.append(float(parallel_re.search(output).group(1)))

        parallel_times[threads].append(sum(run_temp_parallel) / num_runs)

# ------------------ PLOTTING ------------------

plt.figure(figsize=(10,5))

# Serial line (same for all thread counts)
plt.plot(polyonomial_degrees, serial_time,
         marker='o', linewidth=2, label="Serial", color="black")

# Parallel lines for each thread count
for t in thread_num:
    plt.plot(polyonomial_degrees, parallel_times[t],
             marker='o', label=f"Parallel ({t} threads)")

plt.xlabel("Polynomial Degree")
plt.ylabel("Time (seconds)")
plt.title("Polynomial Multiplication Performance")
plt.legend()
plt.xscale("log")
plt.grid(True)

plt.savefig("plot.png")
