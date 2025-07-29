
# MINTO: Jij Management and Insight tool for Optimization

[![PyPI version shields.io](https://img.shields.io/pypi/v/minto.svg)](https://pypi.python.org/pypi/minto/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/minto.svg)](https://pypi.python.org/pypi/minto/)
[![PyPI implementation](https://img.shields.io/pypi/implementation/minto.svg)](https://pypi.python.org/pypi/minto/)
[![PyPI format](https://img.shields.io/pypi/format/minto.svg)](https://pypi.python.org/pypi/minto/)
[![PyPI license](https://img.shields.io/pypi/l/minto.svg)](https://pypi.python.org/pypi/minto/)
[![PyPI download month](https://img.shields.io/pypi/dm/minto.svg)](https://pypi.python.org/pypi/minto/)
[![Downloads](https://pepy.tech/badge/minto)](https://pepy.tech/project/minto)

[![codecov](https://codecov.io/gh/Jij-Inc/minto/graph/badge.svg?token=ZhfvFdt1sJ)](https://codecov.io/gh/Jij-Inc/minto)


`minto` is a Python library designed for developers working on research and development or proof-of-concept experiments using mathematical optimization. Positioned similarly to mlflow in the machine learning field, `minto` provides features such as saving optimization results, automatically computing benchmark metrics, and offering visualization tools for the results.

Primarily supporting Ising optimization problems,  plans to extend its support to a wide range of optimization problems, such as MIP solvers, in the future.

## Key Features

- **Real-time Logging**: Comprehensive logging system for monitoring experiment progress with automatic console output
- **Automatic Environment Metadata Collection**: Automatically captures system information (OS, hardware, Python environment, package versions) for reproducible experiments
- **Flexible Experiment Management**: Easy logging of problems, parameters, solutions, and results
- **Multiple Storage Formats**: Support for both directory-based storage and OMMX archives
- **Comprehensive Benchmarking**: Built-in support for standard optimization problems and performance metrics
- **Data Analysis Tools**: Integrated table generation and visualization capabilities

## Installation
`minto` can be easily installed using pip.

``` shell
pip install minto
```

## Quick Start

Here's a simple example showing how to use MINTO with automatic environment metadata collection and real-time logging:

```python
import minto

# Create an experiment with environment metadata and logging enabled
experiment = minto.Experiment(
    name="my_optimization_experiment",
    collect_environment=True,  # Automatically collects system info
    verbose_logging=True       # Enable real-time logging to console
)

# Log your optimization problem and parameters
experiment.log_parameter("algorithm", "simulated_annealing")
experiment.log_parameter("temperature", 1000)

# Run your optimization experiments
for iteration in range(5):
    with experiment.run():
        # Log parameters for this specific run
        experiment.log_parameter("iteration", iteration)
        
        # Your optimization code here
        result = run_optimization()  # Your optimization function
        
        # Log results
        experiment.log_parameter("objective_value", result.objective)
        experiment.log_parameter("solve_time", result.time)

# The console output will show real-time progress:
# [2025-07-17 10:36:51] 🚀 Starting experiment 'my_optimization_experiment'
# [2025-07-17 10:36:51]   ├─ 🏃 Created run #0
# [2025-07-17 10:36:51]       ├─ 📝 Parameter: iteration = 0
# [2025-07-17 10:36:51]       ├─ 📝 Parameter: objective_value = -42.5
# [2025-07-17 10:36:52]   ├─ ✅ Run #0 completed (0.2s)
# [2025-07-17 10:36:52] 🎯 Experiment completed: 5 runs, total time: 1.2s

# View experiment results including environment information
print("Environment Information:")
experiment.print_environment_summary()

print("\nExperiment Results:")
results_table = experiment.get_run_table()
print(results_table)

# Save experiment (environment metadata automatically included)
experiment.save()
```

The environment metadata automatically captured includes:
- Operating system and version
- Hardware specifications (CPU, memory)
- Python version and virtual environment
- Package versions for key optimization libraries
- Execution timestamp

This ensures your experiments are fully reproducible and comparable across different environments.

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and development.

### Setting up development environment

1. Install uv if you haven't already:
   ```shell
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. Clone the repository and set up the development environment:
   ```shell
   git clone https://github.com/Jij-Inc/MINTO-Public.git
   cd minto
   uv sync --extra dev --extra test --extra docs
   ```

3. Run tests:
   ```shell
   uv run pytest
   ```

4. Run linting and formatting:
   ```shell
   uv run black .
   uv run isort .
   ```

## Documentation and Support

Documentation: https://jij-inc.github.io/minto/

Tutorials will be provided in the future. Stay tuned!


## How to Contribute

See [CONTRIBUITING.md](CONTRIBUTING.md) 

---

Copyright (c) 2023 Jij Inc.

