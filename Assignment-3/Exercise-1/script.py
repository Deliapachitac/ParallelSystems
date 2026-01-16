import subprocess
import os
import re
import statistics
import matplotlib.pyplot as plt

RUNNER = "mpiexec -f machines -n"
EXECUTABLE = "./solution"
ITERATIONS = 4

GRAPH_DIR = "graphs"

# Test Case Parameters
polyonomial_degrees = [10**2, 10**3, 10**4, 10**5]
processes = [2, 4, 8]

def parse_output(output_str):
    """Extract timing metrics from program output."""
    patterns = {
        "serial": r"Serial multiplication time: ([\d.]+) seconds",
        "total": r"Total multiplication time: ([\d.]+) seconds",
        "sending": r"Sending data time: ([\d.]+) seconds",
        "parallel": r"Parallel computation time: ([\d.]+) seconds",
        "receiving": r"Receiving data time: ([\d.]+) seconds"
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

    for sz in polyonomial_degrees:
        print(f"Running: Size {sz} ")
        for th in processes:
            samples = {"serial": [], "total": [], "sending": [], "parallel": [], "receiving": []}
            print(f"    {th} processes")

            for i in range(ITERATIONS):
                print(f"        RUN {i+1}/{ITERATIONS}")
                try:
                    # Command: mpiexec -f machines -n <th> ./solution <sz>
                    command = RUNNER.split() + [str(th), EXECUTABLE, str(sz)]
                    result = subprocess.run(command, capture_output=True, text=True, check=True)

                    metrics = parse_output(result.stdout)

                    for k in samples:
                        samples[k].append(metrics[k])

                except Exception as e:
                    print(f"Error at Size {sz}, Processes {th}: {e}")
                    continue

            avg_metrics = {k: statistics.mean(v) if v else 0 for k, v in samples.items()}

            all_data.append({
                "n": sz,
                "processes": th,
                **avg_metrics
            })

   
    generate_graphs(all_data)


def generate_graphs(data):
    """Generate visualization graphs from benchmark data."""
    
    
    # 1 Serial vs Parallel Computation Time Comparison
    plt.figure(figsize=(14, 7))
    x_pos = 0
    width = 0.35
    xtick_labels = []
    xtick_positions = []
    
    for deg in polyonomial_degrees:
        deg_data = sorted([d for d in data if d['n'] == deg], key=lambda x: x['processes'])
        
        for i, entry in enumerate(deg_data):
            
            plt.bar(x_pos, entry['serial'], width, label='Serial' if x_pos == 0 else '', 
                   color='#d62728', alpha=0.8)
                   
            plt.bar(x_pos + width, entry['parallel'], width, label='Parallel' if x_pos == 0 else '', 
                   color='#2ca02c', alpha=0.8)
            
            
            label = f"n={entry['n']}\nP={entry['processes']}"
            xtick_positions.append(x_pos + width / 2)
            xtick_labels.append(label)
            
            x_pos += 2 * width + 0.2
        
        x_pos += 0.5
    
    plt.xticks(xtick_positions, xtick_labels, fontsize=10)
    plt.xlabel('Problem Size (n) & Process Count (P)', fontsize=12, fontweight='bold')
    plt.ylabel('Time (seconds)', fontsize=12)
    plt.title('Serial vs Parallel Computation Time', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(f"{GRAPH_DIR}/serial_vs_parallel.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {GRAPH_DIR}/serial_vs_parallel.png")
    
    # 2. Communication and Computation Breakdown
    plt.figure(figsize=(14, 7))
    x_pos = 0
    width = 0.25
    xtick_labels = []
    xtick_positions = []
    
    for deg in polyonomial_degrees:
        deg_data = sorted([d for d in data if d['n'] == deg], key=lambda x: x['processes'])
        
        for entry in deg_data:
            plt.bar(x_pos, entry['sending'], width, label='Sending' if x_pos == 0 else '', 
                   color='#1f77b4', alpha=0.8)
            plt.bar(x_pos + width, entry['parallel'], width, label='Parallel Comp' if x_pos == 0 else '', 
                   color='#ff7f0e', alpha=0.8)
            plt.bar(x_pos + 2*width, entry['receiving'], width, label='Receiving' if x_pos == 0 else '', 
                   color='#2ca02c', alpha=0.8)
            
            label = f"n={entry['n']}\nP={entry['processes']}"
            xtick_positions.append(x_pos + width)
            xtick_labels.append(label)
            
            x_pos += 3 * width + 0.2
        
        x_pos += 0.5
    
    plt.xticks(xtick_positions, xtick_labels, fontsize=10)
    plt.xlabel('Problem Size (n) & Process Count (P)', fontsize=12, fontweight='bold')
    plt.ylabel('Time (seconds)', fontsize=12)
    plt.title('Communication and Computation Time Breakdown', fontsize=14, fontweight='bold')
    plt.legend(fontsize=11, loc='upper left')
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(f"{GRAPH_DIR}/communication_breakdown.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {GRAPH_DIR}/communication_breakdown.png")
    
    # 3. Time Components vs Process Count (line plot for each array size)
    for deg in polyonomial_degrees:
        plt.figure(figsize=(12, 7))
        deg_data = sorted([d for d in data if d['n'] == deg], key=lambda x: x['processes'])
        
        if deg_data:
            procs = [d['processes'] for d in deg_data]
            sending = [d['sending'] for d in deg_data]
            parallel = [d['parallel'] for d in deg_data]
            receiving = [d['receiving'] for d in deg_data]
            
            plt.plot(procs, sending, marker='o', linewidth=2.5, markersize=8, label='Sending Time', color='#1f77b4')
            plt.plot(procs, parallel, marker='s', linewidth=2.5, markersize=8, label='Parallel Computation', color='#ff7f0e')
            plt.plot(procs, receiving, marker='^', linewidth=2.5, markersize=8, label='Receiving Time', color='#2ca02c')
            
            plt.xlabel('Number of Processes', fontsize=12, fontweight='bold')
            plt.ylabel('Time (seconds)', fontsize=12)
            plt.title(f'Communication & Computation Time vs Process Count (n={deg})', fontsize=14, fontweight='bold')
            plt.legend(fontsize=11, loc='best')
            plt.grid(True, alpha=0.3)
            plt.xticks(procs)
            plt.tight_layout()
            plt.savefig(f"{GRAPH_DIR}/time_components_n{deg}.png", dpi=300, bbox_inches='tight')
            plt.close()
            print(f"Saved: {GRAPH_DIR}/time_components_n{deg}.png")
    
    # 2a. Data Table without Serial (includes derived total = sending + receiving + parallel and improvement)
    fig, ax = plt.subplots(figsize=(18, 8))
    ax.axis('tight')
    ax.axis('off')

    table_data = []
    headers = ['n', 'Processes', 'Total (s)', 'Sending (s)', 'Parallel (s)', 'Receiving (s)']

    for row in data:
        derived_total = row['sending'] + row['receiving'] + row['parallel']
        table_data.append([
            f"{row['n']}",
            f"{row['processes']}",
            f"{derived_total:.6f}",
            f"{row['sending']:.6f}",
            f"{row['parallel']:.6f}",
            f"{row['receiving']:.6f}"
        ])

    table = ax.table(cellText=table_data, colLabels=headers, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')

    for i in range(1, len(table_data) + 1):
        for j in range(len(headers)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')

    plt.title('Timing (Total = Sending + Parallel + Receiving)', fontsize=16, fontweight='bold', pad=20)
    plt.savefig(f"{GRAPH_DIR}/timing_table_no_serial.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {GRAPH_DIR}/timing_table_no_serial.png")

    # 2b. Data Table with Serial and Parallel (and improvement)
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axis('tight')
    ax.axis('off')

    serial_table = []
    serial_headers = ['n', 'Processes', 'Serial (s)', 'Total (s)', 'Improvement (serial/total)']
    for row in data:
        derived_total = row['sending'] + row['parallel'] + row['receiving']
        improvement_sp = (row['serial'] / derived_total) if derived_total > 0 else 0.0
        serial_table.append([
            f"{row['n']}",
            f"{row['processes']}",
            f"{row['serial']:.6f}",
            f"{derived_total:.6f}",
            f"{improvement_sp:.2f}x"
        ])

    table = ax.table(cellText=serial_table, colLabels=serial_headers, cellLoc='center', loc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)

    for i in range(len(serial_headers)):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')

    for i in range(1, len(serial_table) + 1):
        for j in range(len(serial_headers)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#f0f0f0')

    plt.title('Serial Timing Only', fontsize=16, fontweight='bold', pad=20)
    plt.savefig(f"{GRAPH_DIR}/timing_table_serial_only.png", dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {GRAPH_DIR}/timing_table_serial_only.png")


if __name__ == "__main__":
    run_benchmarks()
