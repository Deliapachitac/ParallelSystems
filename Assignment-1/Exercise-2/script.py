import subprocess
import matplotlib.pyplot as plt
import re


programs = ["./mutex", "./rwlock", "./atomic"]
threads = 4
iterations = 1000
runs = 5

total_time_re = re.compile(r"Time taken for [a-z]+ increment: ([0-9.]+) seconds")
for program in programs:
    print(f"Running benchmark for {program}")

    # Arrays to store times
    total_times = []

    for run in range(runs):
        print(f"  Run {run + 1}/{runs}")
        result = subprocess.run([program, str(threads), str(iterations)],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True)
        output = result.stdout

        # Extract total time using regex
        total_time = float(total_time_re.search(output).group(1))
        total_times.append(total_time)
        
    avg_total_time = sum(total_times) / len(total_times)
    print(f"Average Total Time for {program}: {avg_total_time:.6f} seconds\n")