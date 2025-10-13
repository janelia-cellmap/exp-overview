# Dataset Tracking Feature

## Overview

The `generate_overview_csv.py` script has been enhanced to track which datasets and crops are used in each experiment run. This provides better visibility into data usage across all training experiments.

## New Features

### 1. Dataset Usage Column in CSV

The `auto_generated_overview.csv` now includes a new column: **"Datasets Used"**

This column contains a summary in the format:
```
dataset1: X crops; dataset2: Y crops; dataset3: Z crops
```

Example:
```
jrc_c-elegans-P3_E5_D1_N2: 5; jrc_c-elegans-bw-1: 4; jrc_c-elegans-comma-1: 12
```

### 2. Data Usage Overview YAML

A new file `data/processed/data_usage_overview.yaml` is generated that provides detailed information about which specific crops are used for each dataset in each run.

**Structure:**
```yaml
setup_name:
  dataset_name:
    - crop1
    - crop2
    - crop3
  another_dataset:
    - crop4
    - crop5
```

**Example:**
```yaml
setup_20:
  jrc_c-elegans-P3_E5_D1_N2:
  - crop1047
  - crop1048
  - crop1049
  - crop1050
  - crop1051
  jrc_c-elegans-bw-1:
  - crop518
  - crop519
  - crop540
  - crop550
```

## How It Works

1. **Config Parsing**: The script reads each run's `config.yaml` file to find the `paths.yaml_file` reference
2. **YAML File Location**: It searches for the referenced YAML file in multiple locations:
   - Run directory itself
   - Parent directory's `preparation/yamls/generated/`
   - Parent directory's `yamls/`
3. **Dataset Extraction**: From the YAML file, it extracts:
   - All dataset names
   - All crops for each dataset (excluding special entries like `inference_upscale`, `raw`, `contrast`)
4. **Crop Counting**: Counts the number of crops per dataset
5. **Output Generation**: Creates both the CSV summary and detailed YAML file

## Usage

Simply run the script as before:

```bash
cd /groups/cellmap/cellmap/zouinkhim/exp-overview
python scripts/generate_overview_csv.py
```

This will generate:
- `data/processed/auto_generated_overview.csv` (with Datasets Used column)
- `data/processed/data_usage_overview.yaml` (detailed crop listings)

## Benefits

1. **Quick Overview**: See at a glance how many crops from each dataset are used in each run
2. **Detailed Tracking**: Know exactly which crops are used for reproducibility
3. **Data Auditing**: Identify which datasets are heavily used vs underutilized
4. **Experiment Planning**: Make informed decisions about data allocation for new experiments

## File Locations

- CSV Output: `data/processed/auto_generated_overview.csv`
- YAML Output: `data/processed/data_usage_overview.yaml`
- Script: `scripts/generate_overview_csv.py`
