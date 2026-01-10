import subprocess
import os
import re
import statistics
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
import seaborn as sns

# Configuration
EXECUTABLE = "./../build/Exercise-2/Solution2"
GRAPH_DIR = "graphs"
ITERATIONS = 4

# Test Case Parameters
SIZES = [1000, 5000, 10000]
SPARSITIES = [0, 50, 75, 90, 99]
THREADS = [2, 4]
LOOPS = [1, 10,  20]

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
    df = pd.DataFrame(data)
    sns.set_theme(style="darkgrid")
    
    # --- GLOBAL CALCULATIONS ---
    df['csr_total'] = df['init'] + df['csr']
    df['speedup'] = df['dense'] / df['csr_total']
    df['init_pct'] = (df['init'] / df['csr_total'].replace(0, 1)) * 100
    
    # Standard filters for baseline graphs
    df_5000_4th = df[(df['size'] == 5000) & (df['threads'] == 4)].copy()

    # --- 1 & 2. Performance Baselines (Sparsity) ---
    for name, col, pal, title in [
        ("1_csr_total", "csr_total", "bright", "CSR Total Time"),
        ("2_dense_vs", "dense", "autumn", "Dense Matrix Performance")
    ]:
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_5000_4th, x='sparsity', y=col, hue='loops', 
                     marker='o', palette=pal, linewidth=2.5)
        plt.title(f'{title} vs. Sparsity\n[Size: 5000, 4 Threads]', fontsize=14, fontweight='bold')
        plt.legend(title="Iterations")
        plt.savefig(f"{GRAPH_DIR}/{name}_vs_sparsity.png", dpi=300)
        plt.close()

    # --- 3. CSR Overhead Breakdowns---
    overhead_configs = [
        {"size": 5000, "loops": 10, "label": "3a_overhead_5k_10lp"},
        {"size": 5000, "loops": 20, "label": "3b_overhead_5k_20lp"},
        {"size": 10000, "loops": 10, "label": "3c_overhead_10k_10lp"}
    ]

    for config in overhead_configs:
        plt.figure(figsize=(10, 6))
        sub = df[(df['size'] == config['size']) & 
                 (df['loops'] == config['loops']) & 
                 (df['threads'] == 4)].reset_index(drop=True)
        
        if not sub.empty:
            p1 = plt.bar(sub['sparsity'].astype(str), sub['init'], color='#1f77b4', label='CSR Initialization')
            p2 = plt.bar(sub['sparsity'].astype(str), sub['csr'], bottom=sub['init'], color='#ff7f0e', label='CSR Multiplication')
            
            for i in range(len(sub)):
                pct = sub.loc[i, 'init_pct']
                total_h = sub.loc[i, 'csr_total']
                plt.text(i, total_h + (total_h * 0.01), f'{pct:.1f}% Init', 
                         ha='center', va='bottom', fontsize=9, fontweight='bold', color='#1f77b4')

            plt.title(f"Initialization Overhead: {config['size']}x{config['size']} Matrix\n[{config['loops']} Loops, 4 Threads]", fontsize=13, fontweight='bold')
            plt.ylabel('Total Time (s)')
            plt.legend()
            plt.savefig(f"{GRAPH_DIR}/{config['label']}.png", dpi=300)
        plt.close()

    # --- 4. Speedup Ratio ---
    plt.figure(figsize=(10, 6))
    df_5000_4th['Loop_Label'] = df_5000_4th['loops'].apply(lambda x: f"{x} Iterations")
    sns.lineplot(data=df_5000_4th, x='sparsity', y='speedup', hue='Loop_Label', 
                 palette="tab10", marker='D', linewidth=3)
    plt.axhline(1, ls='--', color='black', alpha=0.7)
    plt.title('CSR Speedup Factor over Dense\n[Size 5000, 4 Threads]', fontsize=14, fontweight='bold')
    plt.savefig(f"{GRAPH_DIR}/speedup_ratio.png", dpi=300)
    plt.close()

  

    # --- 5. Efficiency Heatmap ---
    plt.figure(figsize=(12, 7))
    df_large = df[df['size'] == 10000]
    if not df_large.empty:
        pivot_data = df_large.pivot_table(index='loops', columns='sparsity', values='speedup', aggfunc='mean')
        sns.heatmap(pivot_data, annot=True, cmap="RdYlGn", center=1.0)
        plt.title('CSR Speedup Landscape (Size 10000)\n[Green = CSR Wins | Red = Dense Wins]', fontsize=15, fontweight='bold')
        plt.savefig(f"{GRAPH_DIR}/best_efficiency_landscape.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    if not os.path.exists(EXECUTABLE):
        print(f"Executable not found at {EXECUTABLE}")
    else:
        run_benchmarks()
