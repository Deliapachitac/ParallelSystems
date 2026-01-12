import subprocess
import os
import re
import statistics
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# Configuration
RUNNER = "mpiexec --hostfile hostfile -n "
EXECUTABLE = "./build/Exercise-2/solution"
EXECUTABLE_SERIAL = "./build/Exercise-2/solution_serial"
GRAPH_DIR = "graphs"
ITERATIONS = 4

# Test Case Parameters
SIZES = [1000, 5000, 10000]
SPARSITIES = [0, 25 ,50, 65,75, 90, 99]
PROCESSES = [1, 4 ,8, 16 ,32, 64 , 116]
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

    # --- DEFINE TARGETED CONFIGURATIONS ---
    # We only run what the generate_visuals function actually filters for.
    target_configs = set()

    # Targets for Plot 1, 2, and 6 (Size 5000, 4 Processes, All Sparsities/Loops)
    for sp in SPARSITIES:
        for lp in LOOPS:
            target_configs.add((5000, sp, 4, lp))

    # Targets for Plot 3 (Size 5000 & 10000, 4 Processes, 10 Loops, All Sparsities)
    for sz in [5000, 10000]:
        for sp in SPARSITIES:
            target_configs.add((sz, sp, 4, 10))

    # Targets for Plot 4 (Size 10000, 90% Sparsity, 10 Loops, All Processes)
    for th in PROCESSES:
        target_configs.add((10000, 90, th, 10))

    # Targets for Plot 5 & 8 (Size 10000, 90% Sparsity, 20 Loops, All Processes)
    for th in PROCESSES:
        target_configs.add((10000, 90, th, 20))

    # Targets for Plot 7 (Size 10000, All Sparsities, All Loops, 4 Processes)
    # Note: Using 4 processes as the representative for the heatmap
    for sp in SPARSITIES:
        for lp in LOOPS:
            target_configs.add((10000, sp, 4, lp))

    # Targets for Plot 9 (All Sizes, 90% Sparsity, 20 Loops, 16 Processes)
    for sz in SIZES:
        target_configs.add((sz, 90, 16, 20))

    total_tasks = len(target_configs)
    print(f"Starting benchmark: {total_tasks} targeted configurations.")

    for i, (sz, sp, th, lp) in enumerate(target_configs, 1):
        samples = {"init": [], "scat_csr": [], "scat_dense": [], "csr": [], "dense": []}
        print(f"[{i}/{total_tasks}] Size:{sz} Sp:{sp}% Thr:{th} Loop:{lp}      ", end="\r")

        for _ in range(ITERATIONS):
            try:
                if th == 1:
                    command = [EXECUTABLE_SERIAL.strip(), str(sz), str(sp), str(lp)]
                else:
                    command = RUNNER.split() + [str(th), EXECUTABLE.strip(), str(sz), str(sp), str(lp)]

                result = subprocess.run(command, capture_output=True, text=True, check=True)
                metrics = parse_output(result.stdout)
                for k in samples: 
                    samples[k].append(metrics[k])
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
    df_over = df[(df['size'] == 10000) & (df['sparsity'] == 90) & (df['loops'] == 20)]
    if not df_over.empty:
        plt.bar(df_over['processes'].astype(str), df_over['scat_csr'], label='Scatter Overhead', color='#9467bd')
        plt.bar(df_over['processes'].astype(str), df_over['csr'], bottom=df_over['scat_csr'], label='Actual Computation', color='#17becf')
        plt.title('Communication Overhead (Scatter) vs Computation\n[Size 10000, 90% Sparsity, 20 Loop]', fontsize=13, fontweight='bold')
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
    # --- 8. CSR Combined Time vs Processes ---
    plt.figure(figsize=(10, 6))
    df_proc_study = df[(df['size'] == 10000) & 
                       (df['sparsity'] == 90) & 
                       (df['loops'] == 20)].copy()
    
    if not df_proc_study.empty:
        # Sort by processes to ensure a clean line plot
        df_proc_study = df_proc_study.sort_values('processes')
        
        sns.lineplot(data=df_proc_study, x='processes', y='csr_combined', 
                     marker='o', markersize=10, color='#2c3e50', linewidth=3)
        
        plt.title('Total CSR Time (Init + Multiplication) vs. Number of Processes\n'
                  '[Size: 10000, 90% Sparsity, 20 Loops]', fontsize=14, fontweight='bold')
        plt.xlabel('Number of MPI Processes', fontsize=12)
        plt.ylabel('Time (seconds)', fontsize=12)
        plt.xticks(PROCESSES) # Ensures all process counts are labeled
        
        # Add labels to the points for clarity
        for x, y in zip(df_proc_study['processes'], df_proc_study['csr_combined']):
            plt.text(x, y, f'{y:.4f}s', color='black', va='bottom', ha='center', fontweight='semibold')

        plt.savefig(f"{GRAPH_DIR}/8_csr_combined_vs_processes.png", dpi=300)
    plt.close()
    # --- 9. CSR Combined vs Dense (Scale Study) ---
    plt.figure(figsize=(10, 6))
    df_scale = df[(df['sparsity'] == 90) & 
                  (df['loops'] == 20) & 
                  (df['processes'] == 16)].copy()
    
    if not df_scale.empty:
        df_scale = df_scale.sort_values('size')
        
        plt.plot(df_scale['size'], df_scale['csr_combined'], 
                 marker='o', label='CSR (Init + Mult)', linewidth=2.5, color='#1f77b4')
        plt.plot(df_scale['size'], df_scale['dense_total'], 
                 marker='s', label='Dense (Total)', linewidth=2.5, color='#d62728')
        
        plt.title('CSR vs Dense Performance Scaling\n'
                  '[16 Processes, 90% Sparsity, 20 Loops]', fontsize=14, fontweight='bold')
        plt.xlabel('Matrix Size ($N \\times N$)', fontsize=12)
        plt.ylabel('Time (seconds)', fontsize=12)
        plt.legend()
        plt.yscale('log') # Useful if time varies significantly between 1k and 10k
        
        plt.savefig(f"{GRAPH_DIR}/9_csr_vs_dense_scaling.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    run_benchmarks()