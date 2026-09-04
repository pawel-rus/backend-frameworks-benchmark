#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: ./scenario1_run.sh [all|node|go|python|java|csharp] [additional python args]"
  echo "Examples:"
  echo "  ./scenario1_run.sh all                  # Run all benchmarks with default 5 runs x 30s"
  echo "  ./scenario1_run.sh python --runs 3      # Run only Python with 3 runs per VU step"
  echo "  ./scenario1_run.sh node --vus 10,100    # Run only Node for specific VUs"
  exit 1
fi

FRAMEWORK=$1
shift

# Detect and use virtual environment if available
if [ -d "venv" ]; then
  PYTHON_BIN="./venv/bin/python3"
  echo "🟢 Python virtual environment detected. Running with $PYTHON_BIN..."
else
  PYTHON_BIN="python3"
fi

# Run the automated python-based benchmark suite in unbuffered mode for real-time logging
$PYTHON_BIN -u run_scenario1.py "$FRAMEWORK" "$@"

# Run plotting script automatically if the required libraries are available
echo ""
echo "📊 Benchmark sequence complete. Auto-regenerating vector plots..."
if $PYTHON_BIN -c "import pandas, matplotlib" 2>/dev/null; then
  $PYTHON_BIN plot_scenario1.py
else
  echo "⚠️  Note: Plots could not be auto-generated because pandas/matplotlib are not installed."
  echo "To generate plots, please install them inside your virtual environment or system:"
  echo "  ./venv/bin/pip install pandas numpy matplotlib"
  echo "Then run: ./scenario1_run.sh all"
fi

