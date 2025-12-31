import subprocess
import os
import re
import statistics
import matplotlib.pyplot as plt
from collections import defaultdict

# Configuration
EXECUTABLE = "./../build/Exercise-2/Solution2"
GRAPH_DIR = "graphs"
ITERATIONS = 4

# Test Case Parameters
SIZES = [1000, 2500, 5000, 7500, 10000]
SPARSITIES = [0, 25, 50, 75, 90, 95, 99]
THREADS = [2, 4, 8, 16]
LOOPS = [1, 5, 10, 15, 20, 25]

def parse_output(output_str):
    """Extracts floating point seconds from the program output using regex."""
    patterns = {
        "init": r"Initialization with CSR format took: ([\d.]+) seconds",
        "csr": r"multiplication with CSR format took: ([\d.]+) seconds",
        "dense": r"multiplication with dense matrix took: ([\d.]+) seconds"
    }
    results = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, output_str)
        results[key] = float(match.group(1)) if match else 0.0
    return results

def run_benchmarks():
    if not os.path.exists(GRAPH_DIR):
        os.makedirs(GRAPH_DIR)

    # Data structure to store all results: data[size][sparsity][threads][loops] = [list of samples]
    # We will store dictionaries of {init, csr, dense}
    all_data = []

    total_configs = len(SIZES) * len(SPARSITIES) * len(THREADS) * len(LOOPS)
    current_config = 0

    print(f"Starting benchmark: {total_configs} total configurations...")

    for sz in SIZES:
        for sp in SPARSITIES:
            for th in THREADS:
                for lp in LOOPS:
                    current_config += 1
                    samples = {"init": [], "csr": [], "dense": []}
                    
                    print(f"[{current_config}/{total_configs}] Size:{sz} Sp:{sp}% Thr:{th} Loop:{lp}", end="\r")

                    for _ in range(ITERATIONS):
                        try:
                            result = subprocess.run(
                                [EXECUTABLE, str(sz), str(sp), str(lp), str(th)],
                                capture_output=True, text=True, check=True
                            )
                            metrics = parse_output(result.stdout)
                            for k in samples: samples[k].append(metrics[k])
                        except Exception as e:
                            print(f"\nError at Size {sz}, Sp {sp}: {e}")
                            continue
                    
                    # Store averaged results for this specific configuration
                    avg_metrics = {k: statistics.mean(v) if v else 0 for k, v in samples.items()}
                    all_data.append({
                        "size": sz, "sparsity": sp, "threads": th, "loops": lp,
                        **avg_metrics
                    })

    print("\nBenchmarking complete. Generating graphs...")
    generate_visuals(all_data)

def generate_visuals(data):
    # --- Graph 1: CSR vs Dense Performance by Sparsity ---
    # Fix: Size=5000, Threads=8, Loops=10
    subset = [d for d in data if d['size'] == 5000 and d['threads'] == 8 and d['loops'] == 10]
    if subset:
        subset.sort(key=lambda x: x['sparsity'])
        plt.figure(figsize=(10, 6))
        plt.plot([d['sparsity'] for d in subset], [d['csr'] for d in subset], 'o-', label='CSR Multiplication')
        plt.plot([d['sparsity'] for d in subset], [d['dense'] for d in subset], 's--', label='Dense Multiplication')
        plt.title('Performance vs. Sparsity (Size 5000, 8 Threads)')
        plt.xlabel('Sparsity (% of Zeros)')
        plt.ylabel('Average Time (s)')
        plt.legend()
        plt.grid(True)
        plt.savefig(f"{GRAPH_DIR}/csr_vs_dense_sparsity.png")

    # --- Graph 2: Thread Scalability (Speedup) ---
    # Fix: Size=10000, Sparsity=90, Loops=10
    subset = [d for d in data if d['size'] == 10000 and d['sparsity'] == 90 and d['loops'] == 10]
    if subset:
        subset.sort(key=lambda x: x['threads'])
        plt.figure(figsize=(10, 6))
        plt.plot([d['threads'] for d in subset], [d['csr'] for d in subset], 'D-', color='purple', label='CSR Time')
        plt.title('Thread Scalability (Size 10000, 90% Sparse)')
        plt.xlabel('Number of Threads')
        plt.ylabel('Time (s)')
        plt.xticks(THREADS)
        plt.grid(True)
        plt.savefig(f"{GRAPH_DIR}/thread_scaling.png")

    # --- Graph 3: Loops vs Time (Linearity Check) ---
    # Fix: Size=5000, Sparsity=75, Threads=8
    subset = [d for d in data if d['size'] == 5000 and d['sparsity'] == 75 and d['threads'] == 8]
    if subset:
        subset.sort(key=lambda x: x['loops'])
        plt.figure(figsize=(10, 6))
        plt.bar([str(d['loops']) for d in subset], [d['csr'] for d in subset], color='teal')
        plt.title('Effect of Loop Count on Execution Time')
        plt.xlabel('Number of Loops')
        plt.ylabel('Total CSR Time (s)')
        plt.savefig(f"{GRAPH_DIR}/loops_impact.png")

if __name__ == "__main__":
    if not os.path.exists(EXECUTABLE):
        print(f"Executable not found at {EXECUTABLE}")
    else:
        run_benchmarks()