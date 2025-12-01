import subprocess
import matplotlib.pyplot as plt
import re
import numpy as np


programs = {
    "pthread_barrier": "./exercise_5_1",
    "mutex_cond": "./exercise_5_2",
    "sense_reversal": "./exercise_5_3"
}

threads = [2, 4, 8,16]
iterations = [50,100 ,1000]
runs = 5


time_re = re.compile(r"Time taken: ([0-9.]+) seconds")

results = {}

for name, path in programs.items():
    results[name] = {}
    for thread_count in threads:
        for iteration_count in iterations:
            print(f"Running {name} with {thread_count} threads and {iteration_count} iterations")

            total_times = []

            for run in range(runs):
                print(f"  Run {run + 1}/{runs}")
                result = subprocess.run([path, str(thread_count), str(iteration_count)],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE,
                                        text=True)
                output = result.stdout

                match = time_re.search(output)
                if match:
                    total_time = float(match.group(1))
                    total_times.append(total_time)

            avg_total_time = sum(total_times) / len(total_times)
            results[name][(thread_count, iteration_count)] = avg_total_time
            print(f"Average Time for {name} (threads={thread_count}, iterations={iteration_count}): {avg_total_time:.6f} seconds\n")

# Plotting results
labels = [f"T{t}/{i}" for t in threads for i in iterations]
x = np.arange(len(labels))
width = 0.25

fig, ax = plt.subplots(figsize=(12,6))

for idx, name in enumerate(programs.keys()):
    y_values = [results[name][(t,i)] for t in threads for i in iterations]
    ax.bar(x + idx*width, y_values, width, label=name)

ax.set_xlabel("Threads-Iterations")
ax.set_ylabel("Average Time (seconds)")
ax.set_title("Barrier Implementations Performance")
ax.set_xticks(x + width)
ax.set_xticklabels(labels, rotation=45)
ax.legend()

plt.tight_layout()
plt.savefig("barrier_times.png", dpi=300)
plt.show()

# Create summary table
table_data = []
for t in threads:
    for i in iterations:
        row = [f"T{t}/{i}"]
        for name in programs.keys():
            row.append(f"{results[name][(t,i)]:.6f}")
        table_data.append(row)

col_labels = ["Threads-Iterations"] + list(programs.keys())

fig2, ax2 = plt.subplots(figsize=(12,4))
ax2.axis('tight')
ax2.axis('off')

table = ax2.table(cellText=table_data, colLabels=col_labels, loc='center')
table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1.2, 1.2)

for (row, col), cell in table.get_celld().items():
    if row == 0:
        cell.set_facecolor("#ccccff")
        cell.set_text_props(weight='bold', color='black')

plt.title("Summary of Average Times (Barrier Implementations)")
plt.savefig("barrier_times_table.png", dpi=300)
plt.show()
