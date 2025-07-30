# RCbench - Reservoir Computing Benchmark Toolkit

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/license-MIT-blue)


**RCbench (Reservoir Computing Benchmark Toolkit)** is a comprehensive Python package for evaluating and benchmarking reservoir computing systems. It provides standardized tasks, flexible visualization tools, and efficient evaluation methods for both physical and simulated reservoirs.

## 🚀 Features

RCbench provides:

-**Multiple Benchmark Tasks:**
  -**NLT (Nonlinear Transformation):** Evaluate reservoir performance on standard nonlinear transformations
  -**NARMA:** Test with Nonlinear Auto-Regressive Moving Average models of different orders
  -**Memory Capacity:** Measure the short and long-term memory capabilities
  -**Sin(x):** Assess reservoir ability to transform a random signal into a nonlinear function that use the input as argument
  -**KernelRank:** Evaluates the nonlinearityof the reservoir
  -**GeneralizationRank:** Evaluates the generalization capabilities of the reservoir

-**Advanced Visualization:**
  -Task-specific plotters with customizable configurations
  -General reservoir properties visualization (input signals, output responses, nonlinearity)
  -Frequency domain analysis of reservoir behavior
  -Target vs. prediction comparison with proper time alignment
  
-**Efficient Data Handling:**
  -Automatic measurement loading and parsing
  -Support for various experimental data formats
  -Feature selection and dimensionality reduction tools
---

## 📂 Project Structure

```plaintext
RCbench/
├── rcbench/
|   |── examples/                  # Example scripts
|   |   ├── example_nlt.py
|   |   ├── example_NARMA.py
|   |   ├── example_sinx.py
|   |   └── example_MC.py
│   ├── measurements/          # Data handling
│   │   ├── dataset.py         # ReservoirDataset class
│   │   ├── loader.py          # Data loading utilities
│   │   └── parser.py          # Data parsing utilities
│   ├── tasks/                 # Reservoir computing tasks
│   │   ├── baseevaluator.py   # Base evaluation methods
│   │   ├── nlt.py             # Nonlinear Transformation
│   │   ├── narma.py           # NARMA tasks
│   │   ├── memorycapacity.py  # Memory Capacity
│   │   ├── sinx.py            # Sin(x) approximation
│   │   └── featureselector.py # Feature selection tools
│   ├── visualization/         # Plotting utilities
│   │   ├── base_plotter.py    # Base plotting functionality
│   │   ├── plot_config.py     # Plot configurations
│   │   ├── nlt_plotter.py     # NLT visualization
│   │   ├── narma_plotter.py   # NARMA visualization
│   │   └── sinx_plotter.py    # Sin(x) visualization
│   └── logger.py              # Logging utilities
└
```
---

## 🔧 Installation

**Install directly from GitHub:**

```bash
pip install rcbench
```


Or, install locally (development mode):

```bash
git clone https://github.com/nanotechdave/RCbench.git
cd RCbench
pip install -e .
```


## 🚦 Usage Example
Here's a quick example demonstrating how to perform an NLT evaluation:

```python
import logging
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

from rcbench import ReservoirDataset
from rcbench import NltEvaluator
from rcbench.visualization.plot_config import NLTPlotConfig
from rcbench.logger import get_logger

logger = get_logger(__name__)
logger.setLevel(logging.INFO)

BASE_DIR = "FILE_PATH"

filenameNLT = "YOUR_FILENAME"

measurement_file_NLT = BASE_DIR / filenameNLT

# Load the data directly using the ReservoirDataset class
dataset = ReservoirDataset(measurement_file_NLT)

# Get information about the electrodes
electrodes_info = dataset.summary()
logger.info(f"Parsed Electrodes: {electrodes_info}")

# Get input and node voltages directly from the dataset
input_elec = electrodes_info['input_electrodes'][0]
input_signal = dataset.get_input_voltages()[input_elec]
time = dataset.time

# Get node voltages (only node electrodes, not input)
nodes_output = dataset.get_node_voltages()
electrode_names = electrodes_info['node_electrodes']

# Create NLT plot configuration
plot_config = NLTPlotConfig(
    save_dir=None,  # Save plots to this directory
    
    # General reservoir property plots
    plot_input_signal=True,         # Plot the input signal
    plot_output_responses=True,     # Plot node responses
    plot_nonlinearity=True,         # Plot nonlinearity of nodes
    plot_frequency_analysis=True,   # Plot frequency analysis
    
    # Target-specific plots
    plot_target_prediction=True,    # Plot target vs prediction results
    
    # Plot styling options
    nonlinearity_plot_style='scatter',
    frequency_range=(0, 20)         # Limit frequency range to 0-20 Hz for clearer visualization
)

# Run NLT evaluation with plot config
evaluatorNLT = NltEvaluator(
    input_signal=input_signal,
    nodes_output=nodes_output,
    time_array=time,
    waveform_type='sine',  
    electrode_names=electrode_names,
    plot_config=plot_config
)


resultsNLT = {}
for target_name in evaluatorNLT.targets:
    try:
        result = evaluatorNLT.run_evaluation(
            target_name=target_name,
            metric='NMSE',
            feature_selection_method='pca',
            num_features='all',
            model="Ridge",
            regression_alpha=0.01,
            train_ratio=0.8,
            plot=False,  # Don't plot during evaluation
        )
        resultsNLT[target_name] = result
        # Print results clearly
        logger.output(f"NLT Analysis for Target: '{target_name}'")
        logger.output(f"  - Metric: {result['metric']}")
        logger.output(f"  - Accuracy: {result['accuracy']:.5f}")
        logger.output(f"  - Selected Features Indices: {[electrode_names[i] for i in result['selected_features']]}")
        logger.output(f"  - Model Weights: {result['model'].coef_}\n")
    except Exception as e:
        logger.error(f"Error evaluating {target_name}: {str(e)}")

evaluatorNLT.plot_results(existing_results=resultsNLT)
```

## 📈 Visualization Tools
RCbench features a unified visualization system with:
-**Task-Specific Plotters:** Dedicated plotters for each task (NLTPlotter, NarmaPlotter, SinxPlotter)
-**Customizable Configurations:** Control which plots to generate through configuration objects
-**Comprehensive Visualization:** For each task, view:
  -General reservoir properties (input signals, node responses, nonlinearity)
  -Frequency domain analysis
  -Target vs. prediction comparisons



## 📝 Contributions & Issues
Contributions are welcome! Please open a pull request or an issue on GitHub.

- Issue Tracker: https://github.com/nanotechdave/RCbench/issues

- Pull Requests: https://github.com/nanotechdave/RCbench/pulls

## 📜 License

RCbench is licensed under the MIT License. See the LICENSE file for details.

