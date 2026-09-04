#!/usr/bin/env python3
import os
import sys
import json
import time
import argparse
import subprocess

# Framework profiles configuration
FRAMEWORKS = {
    "node": {
        "service": "node-fastify",
        "container": "benchmark-node",
        "port": 3001,
        "name": "Node.js (Fastify)"
    },
    "go": {
        "service": "go-fiber",
        "container": "benchmark-go",
        "port": 3002,
        "name": "Go (Fiber)"
    },
    "python": {
        "service": "python-fastapi",
        "container": "benchmark-python",
        "port": 3003,
        "name": "Python (FastAPI)"
    },
    "java": {
        "service": "java-spring",
        "container": "benchmark-java",
        "port": 3004,
        "name": "Java (Spring Boot)"
    },
    "csharp": {
        "service": "csharp-dotnet",
        "container": "benchmark-csharp",
        "port": 3005,
        "name": "C# (.NET 8)"
    }
}

DEFAULT_VUS = [10, 50, 100, 200, 500, 1000, 2000, 3000, 5000, 10000]

def run_command(command, shell=False, check=True):
    """Utility to run system commands and return stdout."""
    result = subprocess.run(command, shell=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {command}\nError: {result.stderr}")
    return result.stdout.strip()

def test_framework(framework_id, runs, duration, vus_list):
    profile = FRAMEWORKS[framework_id]
    csv_filename = f"results_scenario1_{framework_id}.csv"
    
    print("=" * 60)
    print(f" Starting Scenario 1 Benchmarks for: {profile['name']}")
    print(f" Output target: {csv_filename}")
    print(f" Configuration: {runs} runs x {duration} duration per test step")
    print("=" * 60)
    
    # Initialize CSV header only if the file does not exist
    file_exists = os.path.exists(csv_filename)
    if not file_exists:
        with open(csv_filename, "w") as f:
            f.write("vus,run,min,avg,med,p95,p99,max,timeout_rate,rps\n")
    else:
        print(f"-> File '{csv_filename}' already exists. We will APPEND new measurements to it.")
        
    # Clean up existing container to ensure clean state
    print(f"-> Stopping any existing containers for {profile['container']}...")
    subprocess.run(["docker", "rm", "-f", profile['container']], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Build and boot container
    print(f"-> Building and booting {profile['service']}...")
    run_command(["docker", "compose", "up", "-d", "--build", profile['service']])
    
    # Wait for container startup and stabilization
    warmup_sec = 45
    print(f"-> Service booted. Warming up and stabilizing for {warmup_sec} seconds...")
    time.sleep(warmup_sec)
    
    try:
        for vus in vus_list:
            print(f"\n" + "-" * 50)
            print(f" >>> Benchmarking Concurrency: {vus} VUs <<<")
            print("-" * 50)
            
            for run in range(1, runs + 1):
                print(f"   * Run {run}/{runs} with {vus} VUs...")
                
                # Setup output json
                summary_json = "temp_summary.json"
                if os.path.exists(summary_json):
                    os.remove(summary_json)
                
                # Execute k6 load test
                k6_cmd = [
                    "k6", "run",
                    "--no-color",
                    "-e", f"PORT={profile['port']}",
                    "-e", f"VUS={vus}",
                    "-e", f"DURATION={duration}",
                    "--summary-export", summary_json,
                    "k6-scripts/scenario1_concurrency.js"
                ]
                
                # Run k6 (suppressing verbose output to console, capturing errors if any)
                res = subprocess.run(k6_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                
                # Parse JSON output safely
                val_min = val_avg = val_med = val_p95 = val_p99 = val_max = val_rps = val_timeouts = 0.0
                parsed_ok = False
                
                if os.path.exists(summary_json):
                    try:
                        with open(summary_json, "r") as sf:
                            data = json.load(sf)
                        
                        metrics = data.get("metrics", {})
                        duration_vals = metrics.get("http_req_duration", {})
                        reqs_vals = metrics.get("http_reqs", {})
                        timeout_vals = metrics.get("timeout_rate", {})
                        
                        val_min = duration_vals.get("min", 0.0)
                        val_avg = duration_vals.get("avg", 0.0)
                        val_med = duration_vals.get("med", 0.0)
                        val_p95 = duration_vals.get("p(95)", 0.0)
                        val_p99 = duration_vals.get("p(99)", 0.0)
                        val_max = duration_vals.get("max", 0.0)
                        val_rps = reqs_vals.get("rate", 0.0)
                        # The timeout metric tracks fraction of requests timed out (0.0 to 1.0) in the "value" key. Convert to percentage:
                        val_timeouts = timeout_vals.get("value", 0.0) * 100.0
                        
                        parsed_ok = True
                        os.remove(summary_json)
                    except Exception as parse_err:
                        print(f"     Warning: Failed to parse summary JSON: {parse_err}")
                
                if not parsed_ok:
                    print(f"     Warning: k6 did not write summary JSON correctly.")
                    if res.stderr:
                        print(f"     k6 stderr snippet: {res.stderr.strip()[:300]}")
                
                print(f"     [RESULT] Avg Latency: {val_avg:.2f} ms | p99 (Tail): {val_p99:.2f} ms | RPS: {val_rps:.1f}/s | Timeouts: {val_timeouts:.2f}%")
                
                # Write to CSV
                with open(csv_filename, "a") as f:
                    f.write(f"{vus},{run},{val_min:.3f},{val_avg:.3f},{val_med:.3f},{val_p95:.3f},{val_p99:.3f},{val_max:.3f},{val_timeouts:.2f},{val_rps:.2f}\n")
                
                # Cool down to let ports release and server idle
                cool_down = 5
                time.sleep(cool_down)
                
    finally:
        print(f"\n-> Stopping container for {profile['service']}...")
        subprocess.run(["docker", "compose", "stop", profile['service']], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Framework {profile['name']} testing cycle completed.")
        print("-" * 60 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Automated Runner for Framework Concurrency Benchmarks (Scenario 1)")
    parser.add_argument("framework", choices=["all", "node", "go", "python", "java", "csharp"],
                        help="The framework to test or 'all' to test all 5 sequentially")
    parser.add_argument("--runs", type=int, default=5,
                        help="Number of iterations to run for each VU level (default: 5)")
    parser.add_argument("--duration", type=str, default="30s",
                        help="Load test duration per iteration (default: 30s)")
    parser.add_argument("--vus", type=str, default=None,
                        help="Comma-separated list of VU sizes (default: 10,50,100,200,500,1000,2000,3000,5000,10000)")
    
    args = parser.parse_args()
    
    # Process VUs list
    if args.vus:
        vus_list = [int(v) for v in args.vus.split(",")]
    else:
        vus_list = DEFAULT_VUS
        
    target_frameworks = []
    if args.framework == "all":
        target_frameworks = list(FRAMEWORKS.keys())
    else:
        target_frameworks = [args.framework]
        
    print(f"Initiating Scenario 1 Benchmark Suite")
    print(f"Target frameworks: {', '.join([FRAMEWORKS[f]['name'] for f in target_frameworks])}")
    print(f"VU Steps: {vus_list}")
    print(f"Runs per step: {args.runs}")
    print(f"Duration per run: {args.duration}")
    print("-" * 60)
    
    start_time = time.time()
    
    for fw in target_frameworks:
        test_framework(fw, args.runs, args.duration, vus_list)
        
    total_elapsed = time.time() - start_time
    m, s = divmod(total_elapsed, 60)
    h, m = divmod(m, 60)
    print(f"All test runs finished successfully.")
    print(f"Total time elapsed: {int(h)}h {int(m)}m {int(s)}s")
    print("Metrics CSV files are saved in the root directory.")

if __name__ == "__main__":
    main()
