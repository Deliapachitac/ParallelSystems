import subprocess
import matplotlib.pyplot as plt
import re

# Degrees of polynomials and number of threads to test 
polyonomial_degrees = [10**3, 10**4]
thread_num =[4 ,8,16]

# Array to store times
initialization_time = []
serial_time = []
parallel_time = []

# Regex patterns to capture times from output
init_re = re.compile(r"Initialization time: ([0-9.]+) seconds")
serial_re = re.compile(r"Serial multiplication time: ([0-9.]+) seconds")
parallel_re = re.compile(r"Parallel multiplication time: ([0-9.]+) seconds")

num_runs = 5

for degree in polyonomial_degrees:
    print(f"Running for polynomial degree: {degree}")

    # Temporary lists to store averages across threads
    temp_init = []
    temp_serial = []
    temp_parallel = []

    

    for threads in thread_num:

        print(f"  Using {threads} threads")

        # Temporary lists to store times for averaging
        run_temp_init = []
        run_temp_serial = []
        run_temp_parallel = []

        for run in range(num_runs):
            print(f"    Run {run + 1}/{num_runs}")
            result = subprocess.run(["./exercise_1", str(degree), str(threads)],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)
            output = result.stdout

            # Extract times using regex
            run_temp_init.append(float(init_re.search(output).group(1)))
            run_temp_serial.append(float(serial_re.search(output).group(1)))
            run_temp_parallel.append(float(parallel_re.search(output).group(1)))

        # Average over 5 runs for this (degree, threads)
        temp_init.append(sum(run_temp_init) / num_runs)
        temp_serial.append(sum(run_temp_serial) / num_runs)
        temp_parallel.append(sum(run_temp_parallel) / num_runs)

    # Average over different thread counts for this degree
    initialization_time.append(sum(temp_init) / len(thread_num))
    serial_time.append(sum(temp_serial) / len(thread_num))
    parallel_time.append(sum(temp_parallel) / len(thread_num))

# Example plot: Serial vs Parallel time
plt.figure(figsize=(10,5))
plt.plot(polyonomial_degrees, serial_time, marker='o', label="Serial")
plt.plot(polyonomial_degrees, parallel_time, marker='s', label="Parallel")
plt.xlabel("Polynomial Degree")
plt.ylabel("Time (seconds)")
plt.title("Polynomial Multiplication Performance")
plt.legend()
plt.xscale("log")
plt.grid(True)
plt.show()
