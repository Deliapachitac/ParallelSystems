import subprocess
import matplotlib.pyplot as plt
import re

# Degrees of polynomials and number of threads to test 
polyonomial_degrees = [10**3, 10**4, 10**5, 10**6, 10**7]
thread_num =[2,4 , 8,16]

# Array to store times
initialization_time = []
serial_time = []
parallel_time = []

# Regex patterns to capture times from output
init_re = re.compile(r"Initialization time: ([0-9.]+) seconds")
serial_re = re.compile(r"Serial multiplication time: ([0-9.]+) seconds")
parallel_re = re.compile(r"Parallel multiplication time: ([0-9.]+) seconds")

for degree in polyonomial_degrees:
    print(f"Running for polynomial degree: {degree}")

    # Temporary lists to store times for averaging
    temp_init = []
    temp_serial = []
    temp_parallel = []

    for threads in thread_num:
        print(f"  Using {threads} threads")
        result = subprocess.run(["./exercise_1", str(degree), str(threads)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)
        output = result.stdout

        # Extract times using regex
        temp_init.append(float(init_re.search(output).group(1)))
        temp_serial.append(float(serial_re.search(output).group(1)))
        temp_parallel.append(float(parallel_re.search(output).group(1)))

    # Compute average times for current degree
    initialization_time.append(sum(temp_init) / len(temp_init))
    serial_time.append(sum(temp_serial) / len(temp_serial))
    parallel_time.append(sum(temp_parallel) / len(temp_parallel))


# print("Average Initialization Times:", initialization_time)
# print("Average Serial Multiplication Times:", serial_time)
# print ("Average Parallel Multiplication Times:", parallel_time)