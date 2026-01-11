import subprocess
import os
import re
import statistics
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Configuration
RUNNER = "mpiexec -n "
EXECUTABLE = "./build/Exercise-2/solution"
EXECUTABLE_SERIAL = "./build/Exercise-2/solution_serial"
GRAPH_DIR = "graphs"
ITERATIONS = 4

# Test Case Parameters
SIZES = [1000, 5000, 10000]
SPARSITIES = [0, 50, 75, 90, 99]
PROCESSES = [1, 2, 4, 8]
LOOPS = [1, 10, 20]

def parse_output(output_str):
    """Extracts all metrics including new Scattering lines."""
    patterns = {
        "init": r"Initialization with CSR format took: ([\d.]+) seconds",
        "scat_csr": r"Scattering the necessary data for CSR took: ([\d.]+) seconds",
        "scat_dense": r"Scattering the necessary data for dense Matrix took: ([\d.]+) seconds",
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

    total_configs = len(SIZES) * len(SPARSITIES) * len(PROCESSES) * len(LOOPS)
    current_config = 0

    print(f"Starting benchmark: {total_configs} total configurations...")

    for sz in SIZES:
        for sp in SPARSITIES:
            for th in PROCESSES:
                for lp in LOOPS:
                    current_config += 1
                    samples = {"init": [], "scat_csr": [], "scat_dense": [], "csr": [], "dense": []}
                    
                    print(f"[{current_config}/{total_configs}] Size:{sz} Sp:{sp}% Thr:{th} Loop:{lp}", end="\r")

                    for _ in range(ITERATIONS):
                        try:
                            # --- 1 PROCESS SPECIAL CASE (SERIAL) ---
                            if th == 1:
                                command = [EXECUTABLE_SERIAL.strip(), str(sz), str(sp), str(lp)]
                            else:
                                # Normal MPI command
                                command = RUNNER.split() + [str(th), EXECUTABLE.strip(), str(sz), str(sp), str(lp)]

                            result = subprocess.run(command, capture_output=True, text=True, check=True)
                            metrics = parse_output(result.stdout)
                            for k in samples: samples[k].append(metrics[k])
                        except Exception as e:
                            print(f"\nError at Size {sz}, Sp {sp}, Thr {th}: {e}")
                            continue
                    
                    avg_metrics = {k: statistics.mean(v) if v else 0 for k, v in samples.items()}
                    all_data.append({
                        "size": sz, "sparsity": sp, "processes": th, "loops": lp,
                        **avg_metrics
                    })

    print("\nBenchmarking complete. Generating graphs...")
    generate_visuals(all_data)

def generate_visuals(data):
    df = pd.DataFrame(data)
    sns.set_theme(style="darkgrid")
    
    # --- CALCULATIONS ---
    df['csr_combined'] = df['init'] + df['csr']
    df['csr_total'] = df['init'] + df['scat_csr'] + df['csr']
    df['dense_total'] = df['scat_dense'] + df['dense']
    df['speedup'] = df['dense'] / df['csr_combined'].replace(0, 1) # Pure computation speedup
    df['init_pct'] = (df['init'] / df['csr_total'].replace(0, 1)) * 100
    
    # Baseline Filter
    df_5000_4th = df[(df['size'] == 5000) & (df['processes'] == 4)].copy()

    # --- 1 & 2. Performance Baselines (Sparsity) ---
    for name, col, pal, title in [
        ("1_csr_total", "csr_total", "bright", "CSR Full Execution Time"),
        ("2_dense_total", "dense_total", "autumn", "Dense Full Execution Time")
    ]:
        plt.figure(figsize=(10, 6))
        sns.lineplot(data=df_5000_4th, x='sparsity', y=col, hue='loops', 
                     marker='o', palette=pal, linewidth=2.5)
        plt.title(f'{title} vs. Sparsity\n[Size: 5000, 4 processes]', fontsize=14, fontweight='bold')
        plt.legend(title="Iterations")
        plt.savefig(f"{GRAPH_DIR}/{name}_vs_sparsity.png", dpi=300)
        plt.close()

    # --- 3. CSR Initialization Overhead ---
    overhead_configs = [
        {"size": 5000, "loops": 10, "label": "3a_overhead_5k_10lp"},
        {"size": 10000, "loops": 10, "label": "3c_overhead_10k_10lp"}
    ]
    for config in overhead_configs:
        plt.figure(figsize=(10, 6))
        sub = df[(df['size'] == config['size']) & (df['loops'] == config['loops']) & (df['processes'] == 4)].reset_index(drop=True)
        if not sub.empty:
            plt.bar(sub['sparsity'].astype(str), sub['init'], color='#1f77b4', label='CSR Initialization')
            plt.bar(sub['sparsity'].astype(str), sub['csr'], bottom=sub['init'], color='#ff7f0e', label='CSR Multiplication')
            plt.title(f"Init Overhead: {config['size']}x{config['size']}\n[{config['loops']} Loops, 4 processes]", fontsize=13, fontweight='bold')
            plt.ylabel('Time (s)')
            plt.legend()
            plt.savefig(f"{GRAPH_DIR}/{config['label']}.png", dpi=300)
        plt.close()

    # --- 4.Data Distribution Comparison (Scattering Time) ---
    plt.figure(figsize=(10, 6))
    df_dist = df[(df['size'] == 10000) & (df['loops'] == 10) & (df['sparsity'] == 90)]
    plt.plot(df_dist['processes'].astype(str), df_dist['scat_csr'], marker='o', label='CSR Scatter Data', color='#2ca02c')
    plt.plot(df_dist['processes'].astype(str), df_dist['scat_dense'], marker='s', label='Dense Scatter Data', color='#d62728')
    plt.title('MPI Distribution Time: CSR vs Dense\n[Matrix Size: 10000, 90% Sparsity]', fontsize=14, fontweight='bold')
    plt.xlabel('MPI Processes')
    plt.ylabel('Seconds')
    plt.legend()
    plt.savefig(f"{GRAPH_DIR}/4_distribution_time.png", dpi=300)
    plt.close()

    # --- 5. Scattering Overhead vs Computation ---
    plt.figure(figsize=(10, 6))
    # Select a case where scattering is significant
    df_over = df[(df['size'] == 5000) & (df['sparsity'] == 99) & (df['loops'] == 20)]
    if not df_over.empty:
        plt.bar(df_over['processes'].astype(str), df_over['scat_csr'], label='Scatter Overhead', color='#9467bd')
        plt.bar(df_over['processes'].astype(str), df_over['csr'], bottom=df_over['scat_csr'], label='Actual Computation', color='#17becf')
        plt.title('Communication Overhead (Scatter) vs Computation\n[Size 5000, 99% Sparsity, 20 Loop]', fontsize=13, fontweight='bold')
        plt.legend()
        plt.savefig(f"{GRAPH_DIR}/5_scatter_overhead_breakdown.png", dpi=300)
    plt.close()

    # --- 6. Speedup Ratio ---
    plt.figure(figsize=(10, 6))
    df_5000_4th['Loop_Label'] = df_5000_4th['loops'].apply(lambda x: f"{x} Iterations")
    sns.lineplot(data=df_5000_4th, x='sparsity', y='speedup', hue='Loop_Label', marker='D', linewidth=3)
    plt.axhline(1, ls='--', color='black', alpha=0.7)
    plt.title('CSR Speedup Factor over Dense\n[Size 5000, 4 processes]', fontsize=14, fontweight='bold')
    plt.savefig(f"{GRAPH_DIR}/speedup_ratio.png", dpi=300)
    plt.close()

    # --- 7. Efficiency Heatmap ---
    plt.figure(figsize=(12, 7))
    df_large = df[df['size'] == 10000]
    if not df_large.empty:
        pivot_data = df_large.pivot_table(index='loops', columns='sparsity', values='speedup', aggfunc='mean')
        sns.heatmap(pivot_data, annot=True, cmap="RdYlGn", center=1.0)
        plt.title('CSR Speedup Landscape (Size 10000)\n[Green = CSR Wins | Red = Dense Wins]', fontsize=15, fontweight='bold')
        plt.savefig(f"{GRAPH_DIR}/best_efficiency_landscape.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    run_benchmarks()