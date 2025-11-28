import subprocess
import matplotlib.pyplot as plt
import re
import numpy as np

programs = ["mutex", "rwlock", "atomic"]
threads = [2, 4, 8]
iterations = [ 10000, 100000, 1000000]
runs = 5

total_time_re = re.compile(r"Time taken for (atomic|mutex|rwlock) increment: ([0-9.]+) seconds")
results = {}

for program in programs:

    results[program] = {}
    for thread_count in threads:
        for iteration_count in iterations:
            print(f"Running program  {program} with {thread_count} threads and {iteration_count} iterations")

            # Arrays to store times
            total_times = []

            for run in range(runs):
                print(f"  Run {run + 1}/{runs}")
                result = subprocess.run(["./exercise_2", program, str(thread_count), str(iteration_count  )],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True)
                output = result.stdout

                # Extract total time using regex
                match = total_time_re.search(output)
                if match:
                    total_time = float(match.group(2))
                    total_times.append(total_time)
        
            #Compute average time of the runs for each 
            avg_total_time = sum(total_times) / len(total_times)
            results[program][(thread_count, iteration_count)] = avg_total_time
            print(f"Average Total Time for {program} (threads={thread_count}, iterations={iteration_count}): {avg_total_time:.6f} seconds\n")


 

labels = [f"T{t}/{i}" for t in threads for i in iterations]
x = np.arange(len(labels))       
width = 0.25            
 
fig, ax = plt.subplots(figsize=(12,6))

# Bars for each program
for idx, program in enumerate(programs):
    y_values = [results[program][(t,i)] for t in threads for i in iterations]
    ax.bar(x + idx*width, y_values, width, label=program)

ax.set_xlabel("Threads-Iterations")
ax.set_ylabel("Average Time (seconds)")
ax.set_title("Atomic vs Mutex vs RWLock")
ax.set_xticks(x + width)
ax.set_xticklabels(labels, rotation=45)
ax.legend()

plt.tight_layout()
plt.savefig("times.png", dpi=300)
plt.show()
