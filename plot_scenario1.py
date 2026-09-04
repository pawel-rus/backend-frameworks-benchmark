#!/usr/bin/env python3
import os
import sys

# Check for required scientific libraries
try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
except ImportError:
    print("=" * 70)
    print("❌ ERROR: Missing required Python packages.")
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
    "p99": {
        "column": "p99",
        "label": "99th Percentile Latency [ms]",
        "title": "Scenario 1: 99th Percentile (Tail) Latency under Concurrency",
        "file": "plot_scenario1_p99.svg",
        "log_y": True
    },
    "p95": {
        "column": "p95",
        "label": "95th Percentile Latency [ms]",
        "title": "Scenario 1: 95th Percentile Latency under Concurrency",
        "file": "plot_scenario1_p95.svg",
        "log_y": True
    },
    "avg": {
        "column": "avg",
        "label": "Average Latency [ms]",
        "title": "Scenario 1: Average Latency under Concurrency",
        "file": "plot_scenario1_avg.svg",
        "log_y": True
    },
    "rps": {
        "column": "rps",
        "label": "Throughput [RPS]",
        "title": "Scenario 1: Throughput (Requests per Second) under Concurrency",
        "file": "plot_scenario1_rps.svg",
        "log_y": False
    },
    "timeout_rate": {
        "column": "timeout_rate",
        "label": "Timeout / Connection Error Rate (%)",
        "title": "Scenario 1: Connection Timeout & Error Rate under Concurrency",
        "file": "plot_scenario1_timeouts.svg",
        "log_y": False
    }
}

def load_data():
    """Load and aggregate CSV data for all frameworks."""
    aggregated_data = {}
    
    for fw_id, meta in FRAMEWORKS.items():
        filename = f"results_scenario1_{fw_id}.csv"
        if not os.path.exists(filename):
            print(f"⚠️  Warning: Telemetry file '{filename}' not found. Skipping {meta['name']}.")
            continue
            
        try:
            df = pd.read_csv(filename)
            # Ensure correct columns and cast VUs to integer
            df['vus'] = df['vus'].astype(int)
            
            # Group by VUs to calculate Mean and Standard Deviation (for confidence bands)
            grouped = df.groupby('vus')
            
            mean_df = grouped.mean()
            std_df = grouped.std().fillna(0) # Standard deviation of single run is 0
            
            aggregated_data[fw_id] = {
                "mean": mean_df,
                "std": std_df,
                "vus": mean_df.index.values
            }
        except Exception as e:
            print(f"❌ Error loading {filename}: {e}")
            
    return aggregated_data

def generate_individual_plots(data):
    """Generate high-quality vector SVG plots for each metric individually."""
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
    
    for metric_key, config in METRICS.items():
        fig, ax = plt.subplots(figsize=(10, 6.5))
        
        has_plots = False
        for fw_id, fw_data in data.items():
            meta = FRAMEWORKS[fw_id]
            vus = fw_data["vus"]
            
            mean_vals = fw_data["mean"][config["column"]].values
            std_vals = fw_data["std"][config["column"]].values
            
            # Plot the main mean line with markers and vertical error bars (whiskers)
            ax.errorbar(vus, mean_vals, yerr=std_vals, label=meta["name"], color=meta["color"], 
                        fmt='o-', linewidth=2, markersize=6, markeredgecolor='white',
                        capsize=4, elinewidth=1.5)
            
            has_plots = True
            
        if not has_plots:
            plt.close(fig)
            continue
            
        # Configure layout and styling (Linear X-axis with rotated labels to prevent overlap)
        ax.set_xlabel('Number of Virtual Users')
        ax.set_ylabel(config["label"])
        
        # Adjust ticks for VUs specifically so they are nice and readable
        all_vus = sorted(list(set([v for fd in data.values() for v in fd["vus"]])))
        if all_vus:
            ax.set_xticks(all_vus)
            ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
            # Set horizontal labels cleanly (rotation=0) since there's plenty of space now
            plt.setp(ax.get_xticklabels(), rotation=0, ha='center')
            
        if config["log_y"]:
            ax.set_yscale('log')
            ax.get_yaxis().set_major_formatter(plt.ScalarFormatter())
            # Hide minor ticks on logarithmic Y-axis to prevent border clutter
            ax.yaxis.set_minor_locator(plt.NullLocator())
        elif metric_key == "rps":
            ax.set_ylim(bottom=0)
            
        ax.grid(False)
        ax.tick_params(axis='both', which='both', direction='out', length=6, width=1.2, colors='#333333')
        ax.legend(loc='best', frameon=True, facecolor='white', edgecolor='#e0e0e0')
        plt.tight_layout()
        
        # Save vector graphics (both SVG and PDF for LaTeX vector compilation)
        fig.savefig(config["file"], format='svg', bbox_inches='tight')
        fig.savefig(config["file"].replace('.svg', '.pdf'), format='pdf', bbox_inches='tight')
        print(f"📈 Generated: {config['file']} and PDF (Vector)")
        plt.close(fig)

def generate_combined_plot(data):
    """Generate a stunning 2x2 combined master chart for papers or thesis reports."""
    if not data:
        return
        
    fig, axs = plt.subplots(2, 2, figsize=(18, 12))
    axs_flat = axs.flatten()
    
    # Use exactly these 4 core metrics for the combined master plot to form a perfect 2x2 grid
    combined_metrics = ["p99", "p95", "avg", "rps"]
    
    for i, metric_key in enumerate(combined_metrics):
        config = METRICS[metric_key]
        ax = axs_flat[i]
        
        for fw_id, fw_data in data.items():
            meta = FRAMEWORKS[fw_id]
            vus = fw_data["vus"]
            
            mean_vals = fw_data["mean"][config["column"]].values
            std_vals = fw_data["std"][config["column"]].values
            
            ax.errorbar(vus, mean_vals, yerr=std_vals, label=meta["name"], color=meta["color"], 
                        fmt='o-', linewidth=2, markersize=4, markeredgecolor='white',
                        capsize=4, elinewidth=1.2)
        ax.set_xlabel('Number of Virtual Users')
        ax.set_ylabel(config["label"])
        ax.set_title(config["title"], fontsize=12, fontweight='bold', pad=10)
        
        # Format ticks
        all_vus = sorted(list(set([v for fd in data.values() for v in fd["vus"]])))
        if all_vus:
            ax.set_xticks(all_vus)
            ax.get_xaxis().set_major_formatter(plt.ScalarFormatter())
            # Set horizontal labels cleanly (rotation=0) in subplots
            plt.setp(ax.get_xticklabels(), rotation=0, ha='center')
            
        if config["log_y"]:
            ax.set_yscale('log')
            ax.get_yaxis().set_major_formatter(plt.ScalarFormatter())
            # Hide minor ticks in subplots log Y-axis
            ax.yaxis.set_minor_locator(plt.NullLocator())
        elif metric_key == "rps":
            ax.set_ylim(bottom=0)
            
        ax.grid(False)
        ax.tick_params(axis='both', which='both', direction='out', length=5, width=1.0, colors='#333333')
        ax.legend(loc='best', frameon=True, facecolor='white', edgecolor='#e0e0e0', fontsize=9)
        
    fig.suptitle("Scenario 1 Master Benchmark: Concurrency, Throughput, and Tail Latency Analysis", 
                 fontsize=18, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    combined_file = "plot_scenario1_combined.svg"
    fig.savefig(combined_file, format='svg', bbox_inches='tight')
    fig.savefig(combined_file.replace('.svg', '.pdf'), format='pdf', bbox_inches='tight')
    print(f"🏆 Generated Combined Master Plot: {combined_file} and PDF (Vector)")
    plt.close(fig)

def generate_rps_vs_latency_plot(data):
    """Generate a stunning academic Throughput vs Latency (RPS vs p99) curve plot."""
    if not data:
        return
        
    fig, ax = plt.subplots(figsize=(10, 6.5))
    
    for fw_id, fw_data in data.items():
        meta = FRAMEWORKS[fw_id]
        
        # Extract mean and std values
        mean_rps = fw_data["mean"]["rps"].values
        mean_p99 = fw_data["mean"]["p99"].values
        std_p99 = fw_data["std"]["p99"].values
        
        # Sort points by RPS to ensure the line is drawn beautifully from left to right
        sorted_indices = np.argsort(mean_rps)
        sorted_rps = mean_rps[sorted_indices]
        sorted_p99 = mean_p99[sorted_indices]
        sorted_std_p99 = std_p99[sorted_indices]
        
        # Plot using errorbar with whiskers
        ax.errorbar(sorted_rps, sorted_p99, yerr=sorted_std_p99, label=meta["name"], color=meta["color"],
                    fmt='o-', linewidth=2, markersize=6, markeredgecolor='white',
                    capsize=4, elinewidth=1.5)
                    
    ax.set_yscale('log')
    ax.get_yaxis().set_major_formatter(plt.ScalarFormatter())
    # Hide minor ticks on Y-axis for rps_vs_latency plot
    ax.yaxis.set_minor_locator(plt.NullLocator())
    ax.set_xlabel('Throughput [RPS]')
    ax.set_ylabel('99th Percentile Latency [ms]')
    ax.grid(False)
    ax.tick_params(axis='both', which='both', direction='out', length=6, width=1.2, colors='#333333')
    ax.legend(loc='best', frameon=True, facecolor='white', edgecolor='#e0e0e0')
    
    plt.tight_layout()
    filename = "plot_scenario1_rps_vs_latency.svg"
    fig.savefig(filename, format='svg', bbox_inches='tight')
    fig.savefig(filename.replace('.svg', '.pdf'), format='pdf', bbox_inches='tight')
    print(f"📈 Generated Throughput-Latency curve: {filename} and PDF (Vector)")
    plt.close(fig)

def main():
    print("=" * 60)
    print("📊 Initiating Visualization Suite for Scenario 1")
    print("=" * 60)
    
    data = load_data()
    
    if not data:
        print("❌ Error: No benchmark CSV telemetry files found.")
        print("Please run the benchmark runner first: python run_scenario1.py all")
        sys.exit(1)
        
    print(f"Found telemetry data for {len(data)} frameworks.")
    
    # Generate individual charts
    generate_individual_plots(data)
    
    # Generate combined 2x2 grid chart
    generate_combined_plot(data)
    
    # Generate Throughput-Latency curve (RPS vs p99)
    generate_rps_vs_latency_plot(data)
    
    print("\n🎉 All publication-ready vector charts successfully generated inside the directory!")
    print("You can embed these SVG files directly into your HTML pages, reports, or LaTeX files.")

if __name__ == "__main__":
    main()
