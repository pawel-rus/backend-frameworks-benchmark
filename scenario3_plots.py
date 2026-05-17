import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import argparse

parser = argparse.ArgumentParser(description='Generate charts from k6 benchmark results.')
parser.add_argument('frameworks', nargs='*', help='Names of frameworks to plot (e.g., go java python)')
args = parser.parse_args()

if args.frameworks:
    csv_files = [f"results_{f.lower()}.csv" for f in args.frameworks]
else:
    csv_files = glob.glob("results_*.csv")

existing_files = [f for f in csv_files if os.path.exists(f)]

if not existing_files:
    print("Error: No matching .csv files found. Check if the names are correct.")
    exit(1)

plt.style.use('seaborn-v0_8-darkgrid')
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

for file in existing_files:
    framework = os.path.basename(file).replace('results_', '').replace('.csv', '').upper()
    df = pd.read_csv(file)
    
    ax1.plot(df['ERROR_RATE'], df['AVG_CPU'], marker='o', linewidth=2, label=framework)
    
    ax2.plot(df['ERROR_RATE'], df['RPS'], marker='s', linewidth=2, label=framework)

ax1.set_title('CPU Usage vs. Exception Handling Overhead', fontsize=14, fontweight='bold')
ax1.set_xlabel('Error Rate', fontsize=12)
ax1.set_ylabel('Average CPU Usage [%]', fontsize=12)
ax1.set_xlim(-0.05, 1.05)
ax1.set_ylim(bottom=0)
ax1.legend(title="Frameworks")

ax2.set_title('Throughput (RPS) vs. Exception Handling Overhead', fontsize=14, fontweight='bold')
ax2.set_xlabel('Error Rate', fontsize=12)
ax2.set_ylabel('Requests per Second (Req/s)', fontsize=12)
ax2.set_xlim(-0.05, 1.05)
ax2.set_ylim(bottom=0)
ax2.legend(title="Frameworks")

plt.tight_layout()

if args.frameworks:
    output_file = f"benchmark_{'_'.join(args.frameworks)}.png"
else:
    output_file = "benchmark_all.png"

plt.savefig(output_file, dpi=300)
print(f"Charts successfully generated and saved as: {output_file}")