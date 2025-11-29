import subprocess 
import matplotlib.pyplot as plt 
import re 
import numpy as np 
# Degrees of polynomials and number of threads to test 
polyonomial_degrees = [ 10**3, 10**4, 10**5 , 10**6] 
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
            result = subprocess.run(["./exercise_1", str(degree), str(threads)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) 
            output = result.stdout 

            # Extract times using regex 
            run_temp_init.append(float(init_re.search(output).group(1))) 
            run_temp_serial.append(float(serial_re.search(output).group(1))) 
            run_temp_parallel.append(float(parallel_re.search(output).group(1)))

        results["Initialization"][(threads, degree)] = sum(run_temp_init) / num_runs
        results["Serial"][(threads, degree)] = sum(run_temp_serial) / num_runs      
        results["Parallel"][(threads, degree)] = sum(run_temp_parallel) / num_runs


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