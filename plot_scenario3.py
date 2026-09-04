#!/usr/bin/env python3
import os
import sys
import numpy as np

# Check for required scientific libraries
try:
    import pandas as pd
    import matplotlib.pyplot as plt
except ImportError:
    print("=" * 70)
    print("ERROR: Missing required Python packages.")
    print("To run the plotting script, please install pandas, numpy, and matplotlib:")
    print("   pip install pandas numpy matplotlib")
    print("=" * 70)
    sys.exit(1)

# Configuration and Styling
FRAMEWORKS = {
    "node": {"name": "Node.js (Fastify)", "color": "#4eaf0a", "marker": "o"},
    "go": {"name": "Go (Fiber)", "color": "#00a2ff", "marker": "o"},
    "python": {"name": "Python (FastAPI)", "color": "#ffc107", "marker": "o"},
    "java": {"name": "Java (Spring Boot)", "color": "#e51c23", "marker": "o"},
    "csharp": {"name": "C# (.NET 8)", "color": "#673ab7", "marker": "o"}
}

METRICS = {
    "RPS": {
        "column": "RPS",
        "label": "Throughput [RPS]",
        "title": "Scenario 3: Throughput vs Error Rate",
        "file": "plot_scenario3_rps.svg",
        "log_y": False
    },
    "AVG_CPU": {
        "column": "AVG_CPU",
        "label": "Average CPU Usage [%]",
        "title": "Scenario 3: Average CPU Usage vs Error Rate",
        "file": "plot_scenario3_cpu.svg",
        "log_y": False
    },
    "P95_LAT": {
        "column": "P95_LAT",
        "label": "95th Percentile Latency [ms]",
        "title": "Scenario 3: 95th Percentile Latency vs Error Rate",
        "file": "plot_scenario3_p95.svg",
        "log_y": False
    },
    "AVG_LAT": {
        "column": "AVG_LAT",
        "label": "Average Latency [ms]",
        "title": "Scenario 3: Average Latency vs Error Rate",
        "file": "plot_scenario3_avg_lat.svg",
        "log_y": False
    }
}

def load_data():
    """Load CSV data for all frameworks."""
    data = {}
    for fw_id, meta in FRAMEWORKS.items():
        filename = f"results_{fw_id}.csv"
        if os.path.exists(filename):
            try:
                # Read data, force decimal dot
                df = pd.read_csv(filename, decimal=".")
                # Sort by ERROR_RATE
                df = df.sort_values(by="ERROR_RATE")
                data[fw_id] = df
            except Exception as e:
                print(f"Error loading {filename}: {e}")
        else:
            print(f"Warning: File {filename} not found. Skipping {meta['name']}.")
    return data

def apply_global_styling():
    """Apply visualization style matching scenario 1."""
    plt.rcParams.update({
        'font.size': 12,
        'axes.labelsize': 13,
        'axes.titlesize': 14,
        'xtick.labelsize': 11,
        'ytick.labelsize': 11,
        'legend.fontsize': 11,
        'figure.titlesize': 16,
        'font.family': 'sans-serif',
        'grid.alpha': 0.3,
        'grid.color': '#cccccc',
        'grid.linestyle': '--'
    })

def generate_individual_plots(data):
    """Generate SVG plots for each metric individually."""
    apply_global_styling()
    
    for metric_key, config in METRICS.items():
        fig, ax = plt.subplots(figsize=(10, 6.5))
        has_plots = False
        
        all_error_rates = set()
        
        for fw_id, df in data.items():
            if config["column"] not in df.columns:
                continue
            meta = FRAMEWORKS[fw_id]
            
            if "RUN" in df.columns:
                grouped = df.groupby("ERROR_RATE")
                mean_df = grouped.mean()
                std_df = grouped.std().fillna(0)
                
                error_rates = mean_df.index.values
                vals = mean_df[config["column"]].values
                yerrs = std_df[config["column"]].values
            else:
                error_rates = df["ERROR_RATE"].values
                vals = df[config["column"]].values
                yerrs = np.zeros_like(vals)
                
            all_error_rates.update(error_rates)
            
            ax.errorbar(error_rates, vals, yerr=yerrs, label=meta["name"], color=meta["color"], 
                        fmt='o-', linewidth=2, markersize=6, markeredgecolor='white',
                        capsize=4, elinewidth=1.5)
            
            has_plots = True
            
        if not has_plots:
            plt.close(fig)
            continue
            
        ax.set_xlabel('Error Rate')
        ax.set_ylabel(config["label"])
        
        all_rates = sorted(list(all_error_rates))
        if all_rates:
            ax.set_xticks(all_rates)
            ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
            plt.setp(ax.get_xticklabels(), rotation=0, ha='center')
            
        if config["log_y"]:
            ax.set_yscale('log')
            ax.get_yaxis().set_major_formatter(plt.ScalarFormatter())
            ax.yaxis.set_minor_locator(plt.NullLocator())
            
        # Optional: ensure linear scale doesn't start from an awkward negative number if close to 0
        if not config["log_y"]:
            bottom, top = ax.get_ylim()
            if bottom < 0 and min([df[config["column"]].min() for df in data.values() if config["column"] in df.columns]) >= 0:
                ax.set_ylim(bottom=0)
            
        ax.grid(True)  # Turn grid on explicitly to look better on linear scale
        ax.tick_params(axis='both', which='both', direction='out', length=6, width=1.2, colors='#333333')
        ax.legend(loc='best', frameon=True, facecolor='white', edgecolor='#e0e0e0')
        plt.tight_layout()
        
        fig.savefig(config["file"], format='svg', bbox_inches='tight')
        fig.savefig(config["file"].replace('.svg', '.pdf'), format='pdf', bbox_inches='tight')
        print(f"Generated: {config['file']} and PDF (Vector)")
        plt.close(fig)

def main():
    print("=" * 60)
    print("Generating plots for Scenario 3")
    print("=" * 60)
    
    data = load_data()
    
    if not data:
        print("Error: No benchmark CSV telemetry files found.")
        print("Please run the benchmark runner first: ./scenario3_run.sh all")
        sys.exit(1)
        
    print(f"Found telemetry data for {len(data)} frameworks.")
    
    # Generate individual charts
    generate_individual_plots(data)
    
    print("\nAll vector charts generated inside the directory.")

if __name__ == "__main__":
    main()