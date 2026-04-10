"""
Fresh run of OpenAI benchmark with forced module reload.
This ensures the truncation fix in embeddings.py takes effect.
"""

import sys
import importlib

# Clear any cached modules
for module in list(sys.modules.keys()):
    if module.startswith('src.'):
        del sys.modules[module]

# Now import and run the benchmark
from test_benchmark_openai import run_benchmark

if __name__ == "__main__":
    run_benchmark()
