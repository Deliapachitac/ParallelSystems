import subprocess
import re
import matplotlib.pyplot as plt
import os
import sys

# ================= CONFIGURATION =================
EXECUTABLE_MUTEX = "./solution"
EXECUTABLE_RW = "./solution_rw"

# Use enough threads to ensure contention (usually equal to or 2x your CPU cores)
FIXED_THREADS = 16 

# --- TUNED SCENARIOS ---
SCENARIOS = [
    {
        # Scenario 1: "The Fight"
        # Very few items means threads constantly collide. 
        # Fine-grained should beat Coarse. RW should shine at high read %.
        "name": "Scenario_High_Contention",
        "title": "High Contention (10 Items, 20k Trans)",
        "items": 10,
        "trans": 20000 
    },
    {
        # Scenario 2: "The Balanced Workload"
        # Standard use case. Collisions happen but not constantly.
        "name": "Scenario_Medium_Contention",
        "title": "Medium Contention (1,000 Items, 20k Trans)",
        "items": 1000,
        "trans": 20000
    },
    {
        # Scenario 3: "The Spread"
        # Huge array. Almost zero collisions. 
        # This tests the "Overhead" of the locks (RW locks usually slower here due to complexity).
        "name": "Scenario_Low_Contention",
        "title": "Low Contention (10k Items, 20k Trans)",
        "items": 10000,
        "trans": 20000
    },
    {
        # Scenario 1: "The Fight"
        # Very few items means threads constantly collide. 
        # Fine-grained should beat Coarse. RW should shine at high read %.
        "name": "Scenario_High_Contention_small",
        "title": "High Contention (10 Items, 2k Trans)",
        "items": 10,
        "trans": 2000 
    },
    {
        # Scenario 2: "The Balanced Workload"
        # Standard use case. Collisions happen but not constantly.
        "name": "Scenario_Medium_Contention_small",
        "title": "Medium Contention (1,000 Items, 2k Trans)",
        "items": 1000,
        "trans": 2000
    },
    {
        # Scenario 3: "The Spread"
        # Huge array. Almost zero collisions. 
        # This tests the "Overhead" of the locks (RW locks usually slower here due to complexity).
        "name": "Scenario_Low_Contention_small",
        "title": "Low Contention (10k Items, 2k Trans)",
        "items": 10000,
        "trans": 2000
    }
]

# --- TUNED READ RATIOS ---
# We focus heavily on the 0.90 - 0.99 range because that is where
# the Read-Write lock theoretically overtakes the Mutex.
READ_RATIOS = [0.0, 0.5, 0.8, 0.9, 0.95, 0.98, 0.99]
# =================================================

def parse_time(output_str):
    """Extracts execution time from the C program output."""
    match = re.search(r"Execution took:\s*([0-9.]+)\s*seconds", output_str)
    if match:
        return float(match.group(1))
    return 0.0

def run_single_test(executable, items, trans, perc, gran, threads):
    """Runs the C executable and returns the time."""
    if not os.path.exists(executable):
        print(f"Error: {executable} not found.")
        return 0.0
    
    # Arguments: [Items] [Trans/Thread] [Read %] [Granularity] [Threads]
    cmd = [executable, str(items), str(trans), str(perc), str(gran), str(threads)]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error running {executable}: {result.stderr}")
            return 0.0
        return parse_time(result.stdout)
    except Exception as e:
        print(f"Exception: {e}")
        return 0.0

def print_and_save_table(title, ratios, results, filename_base):
    """Prints a formatted table to console and saves to .txt"""
    
    header = f"{'Read %':<10} | {'Mut Fine(s)':<12} | {'Mut Crse(s)':<12} | {'RW Fine(s)':<12} | {'RW Crse(s)':<12}"
    sep = "-" * len(header)
    
    output_lines = []
    output_lines.append(f"\nTABLE: {title}")
    output_lines.append(sep)
    output_lines.append(header)
    output_lines.append(sep)

    for i, r in enumerate(ratios):
        mf = results["Mutex_Fine"][i]
        mc = results["Mutex_Coarse"][i]
        rf = results["RW_Fine"][i]
        rc = results["RW_Coarse"][i]
        
        row = f"{int(r*100):<9}% | {mf:<12.4f} | {mc:<12.4f} | {rf:<12.4f} | {rc:<12.4f}"
        output_lines.append(row)
    
    output_lines.append(sep + "\n")

    # Print to Console
    full_text = "\n".join(output_lines)
    print(full_text)
    
    # Save to file
    with open(f"{filename_base}_table.txt", "w") as f:
        f.write(full_text)

def main():
    print(f"--- Starting Benchmarks ({FIXED_THREADS} Threads) ---")
    print("Note: Ensure executables exist and C code uses usleep() if needed.")

    for scenario in SCENARIOS:
        items = scenario["items"]
        trans = scenario["trans"]
        title = scenario["title"]
        name = scenario["name"]
        
        print(f"\nProcessing: {title}")
        
        # Storage
        results = {
            "Mutex_Fine": [], "Mutex_Coarse": [],
            "RW_Fine": [],    "RW_Coarse": []
        }

        # Run Tests
        for p in READ_RATIOS:
            sys.stdout.write(f"\r  > Running Test: Read Ratio {int(p*100)}%   ")
            sys.stdout.flush()
            
            # Mutex (0=Fine, 1=Coarse)
            results["Mutex_Fine"].append(run_single_test(EXECUTABLE_MUTEX, items, trans, p, 0, FIXED_THREADS))
            results["Mutex_Coarse"].append(run_single_test(EXECUTABLE_MUTEX, items, trans, p, 1, FIXED_THREADS))
            
            # RW Lock (0=Fine, 1=Coarse)
            results["RW_Fine"].append(run_single_test(EXECUTABLE_RW, items, trans, p, 0, FIXED_THREADS))
            results["RW_Coarse"].append(run_single_test(EXECUTABLE_RW, items, trans, p, 1, FIXED_THREADS))
        
        print("\n  > Data collected.")

        # 1. Print and Save Table
        print_and_save_table(title, READ_RATIOS, results, name)

        # 2. Generate Plot
        plt.figure(figsize=(10, 6))

        # Plot Lines
        plt.plot(READ_RATIOS, results["Mutex_Fine"], 'r-o',  linewidth=2, label='Mutex (Fine)')
        plt.plot(READ_RATIOS, results["Mutex_Coarse"], 'r--x', linewidth=1.5, alpha=0.7, label='Mutex (Coarse)')
        plt.plot(READ_RATIOS, results["RW_Fine"], 'g-s',  linewidth=2, label='RW Lock (Fine)')
        plt.plot(READ_RATIOS, results["RW_Coarse"], 'g--^', linewidth=1.5, alpha=0.7, label='RW Lock (Coarse)')

        # Styling
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel('Ratio of Read Operations (0.0 - 1.0)', fontsize=12)
        plt.ylabel('Execution Time (seconds)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()
        
        # Save to file
        plt.savefig(f"{name}.png", dpi=150)
        plt.close()
        print(f"  > Graph saved to: {name}.png")

    print("\nAll scenarios completed.")

if __name__ == "__main__":
    main()