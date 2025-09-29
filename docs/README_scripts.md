# Experiment Overview CSV Generator

This repository contains Python scripts to generate and manage the `overview.csv` file that tracks machine learning experiments.

## Files

- `generate_overview_csv.py` - Main script to generate the complete CSV from scratch or add experiments programmatically
- `add_experiment.py` - Interactive script to quickly add new experiments to the existing CSV
- `overview.csv` - The generated CSV file containing experiment data

## Usage

### 1. Generate Complete CSV from Scratch

To regenerate the entire `overview.csv` file with all existing data:

```bash
python generate_overview_csv.py
```

This will create the CSV file with all the existing experiment data.

### 2. Add New Experiments Interactively

To add a new experiment to the existing CSV:

```bash
python add_experiment.py
```

This will prompt you for the experiment details and append them to the CSV file.

### 3. Add Experiments Programmatically

You can also use the `ExperimentOverviewGenerator` class in your own scripts:

```python
from generate_overview_csv import ExperimentOverviewGenerator, ExperimentEntry

# Create generator
generator = ExperimentOverviewGenerator("overview.csv")

# Load existing data
generator.load_existing_data()

# Add new experiment
new_exp = ExperimentEntry(
    group="exp_test",
    setup="setup_new",
    target="mito",
    model_type="fly model",
    starting_checkpoint="from scratch",
    max_iterations=100000,
    resolution_nm=16,
    batch_size=14.0,
    learning_rate=5e-06,
    still_running="YES"
)

generator.add_experiment(new_exp)
generator.write_csv()
```

## CSV Structure

The CSV contains the following columns:

- **Group**: Experiment group (e.g., exp_mito, exp_cell)
- **Setup**: Setup identifier (e.g., setup_15, setup_20)
- **Target**: Target organelle/structure (e.g., mito, nuc, cell)
- **Model Type**: Type of model used (e.g., fly model, isolated_unet)
- **Starting Checkpoint**: Initial checkpoint or "from scratch"
- **Max Iterations**: Maximum training iterations
- **Resolution (nm)**: Training resolution in nanometers
- **Batch Size**: Training batch size
- **Learning Rate**: Learning rate used
- **Creation Date**: Date the experiment was created (YYYY-MM-DD)
- **Still Running**: Whether the experiment is still running (YES/NO)

## Examples

### Example 1: Basic Experiment
```python
experiment = ExperimentEntry(
    group="exp_mito",
    setup="setup_35",
    target="mito",
    model_type="fly model",
    starting_checkpoint="20250806_mito_mouse_distance_16nm/362k",
    max_iterations=500000,
    resolution_nm=16,
    batch_size=14.0,
    learning_rate=5e-06,
    still_running="YES"
)
```

### Example 2: Experiment with Minimal Info
```python
experiment = ExperimentEntry(
    group="exp_test",
    setup="preliminary_test",
    target="various",
    model_type="fly model",
    starting_checkpoint="from scratch",
    still_running="NO"
)
```

## Notes

- Dates are automatically set to today if not specified
- Empty fields are allowed for optional parameters
- The script handles both numeric and string values for iterations and resolution (e.g., "80000+" or "16-64")
- Scientific notation is supported for learning rates (e.g., 5e-06)

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)