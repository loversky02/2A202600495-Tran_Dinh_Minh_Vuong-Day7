#!/usr/bin/env python
"""
Force reload modules and run OpenAI benchmark.
"""
import sys
import importlib

# Remove cached modules
for module in list(sys.modules.keys()):
    if module.startswith('src.'):
        del sys.modules[module]

# Now import and run
from test_benchmark_openai import run_benchmark

if __name__ == "__main__":
    run_benchmark()
