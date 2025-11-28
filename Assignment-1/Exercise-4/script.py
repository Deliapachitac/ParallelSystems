import subprocess
import re
import matplotlib.pyplot as plt
import os

# ================= CONFIGURATION =================
EXECUTABLE_MUTEX = "./solution"
EXECUTABLE_RW = "./solution_rw"
FIXED_THREADS = 4

# Define the 3 Scenarios
SCENARIOS = [
    {
        "name": "Scenario_A_High_Contention",
        "title": "Scenario A: High Contention (Small Array: 100 items)",
        "items": 100,
        "trans": 100000
    },
    {
        "name": "Scenario_B_Low_Contention",
        "title": "Scenario B: Low Contention (Large Array: 10,000 items)",
        "items": 10000,
        "trans": 100000
    },
    {
        "name": "Scenario_C_Heavy_Workload",
        "title": "Scenario C: Heavy Workload (1M Transactions)",
        "items": 1000,
        "trans": 1000000
    }
]

# Read/Write Ratios to test (0.0 = All Writes, 0.99 = Mostly Reads)
READ_RATIOS = [0.0, 0.2, 0.5, 0.8, 0.9, 0.95, 0.99]
# =================================================

def parse_time(output_str):
    match = re.search(r"Execution took:\s*([0-9.]+)\s*seconds", output_str)
    if match:
        return float(match.group(1))
    return None

def run_single_test(executable, items, trans, perc, gran, threads):
    if not os.path.exists(executable):
        return None
    cmd = [executable, str(items), str(trans), str(perc), str(gran), str(threads)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return None
        return parse_time(result.stdout)
    except Exception as e:
        return None

def main():
    print(f"--- Starting Benchmarks ({FIXED_THREADS} Threads) ---")

    for scenario in SCENARIOS:
        # 1. Setup Data Containers
        items = scenario["items"]
        trans = scenario["trans"]
        title = scenario["title"]
        filename = f"{scenario['name']}.png"
        
        print(f"\nProcessing: {title}")
        
        results = {
            "Mutex_Fine": [], "Mutex_Coarse": [],
            "RW_Fine": [],    "RW_Coarse": []
        }

        # 2. Run Tests
        for p in READ_RATIOS:
            print(f"  > Testing Read Ratio {int(p*100)}%...", end="\r")
            
            # Mutex (0=Fine, 1=Coarse)
            results["Mutex_Fine"].append(run_single_test(EXECUTABLE_MUTEX, items, trans, p, 0, FIXED_THREADS))
            results["Mutex_Coarse"].append(run_single_test(EXECUTABLE_MUTEX, items, trans, p, 1, FIXED_THREADS))
            
            # RW Lock (0=Fine, 1=Coarse)
            results["RW_Fine"].append(run_single_test(EXECUTABLE_RW, items, trans, p, 0, FIXED_THREADS))
            results["RW_Coarse"].append(run_single_test(EXECUTABLE_RW, items, trans, p, 1, FIXED_THREADS))
        
        print(f"  > Done gathering data. Generating plot...")

        # 3. Create a NEW Figure for this scenario
        plt.figure(figsize=(10, 6))

        # Plot Lines
        plt.plot(READ_RATIOS, results["Mutex_Fine"], 'r--o', label='Mutex (Fine)')
        plt.plot(READ_RATIOS, results["Mutex_Coarse"], 'r-x', label='Mutex (Coarse)')
        plt.plot(READ_RATIOS, results["RW_Fine"], 'b--o', label='RW Lock (Fine)')
        plt.plot(READ_RATIOS, results["RW_Coarse"], 'b-x', label='RW Lock (Coarse)')

        # Styling
        plt.title(title, fontsize=14, fontweight='bold')
        plt.xlabel('Percentage of Balance Questions (Reads)', fontsize=12)
        plt.ylabel('Execution Time (seconds)', fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.legend()
        
        # Save to file
        plt.savefig(filename, dpi=300) # dpi=300 makes it high quality
        plt.close() # Close memory to start fresh for next loop
        
        print(f"  > Saved graph to: {filename}")

    print("\nAll scenarios completed successfully.")

if __name__ == "__main__":
    main()