
# Experiment Overview Repository

This repository contains tools and data for managing and visualizing machine learning experiment overviews across multiple research projects.

## 📁 Repository Structure

```
exp-overview/
├── README.md                     # This file
├── scripts/                      # Main execution scripts
│   ├── generate_overview_csv.py  # Primary script for generating experiment CSV
│   ├── add_experiment.py         # Script for adding new experiments
│   ├── check_config_targets.py   # Configuration validation
│   ├── fix_csv_comprehensive.py  # Data cleaning utilities
│   └── generate_timeline.py      # Timeline visualization generation
├── data/                         # Data storage
│   ├── raw/                      # Original/manual data files
│   │   └── overview.csv          # Original manual experiment overview
│   └── processed/                # Generated/processed data files
│       ├── auto_generated_overview.csv     # Main automated overview
│       ├── config_targets_check.csv        # Target validation results
│       ├── detailed_setup_analysis.csv     # Detailed experiment analysis
│       └── overview_corrected.csv          # Corrected overview data
├── output/                       # Generated outputs
│   ├── reports/                  # Analysis reports
│   │   └── comparison_report.md  # Data accuracy comparison report
│   └── visualizations/           # HTML visualizations
│       ├── index.html            # Main dashboard
│       ├── experiment_timeline.html  # Timeline view
│       ├── experiment_gantt.html     # Gantt chart view
│       └── experiment_stats.html     # Statistics dashboard
├── config/                       # Configuration files
│   └── requirements.txt          # Python dependencies
├── docs/                         # Documentation
│   └── README_scripts.md         # Detailed script documentation
├── archive/                      # Archived/temporary files
└── .github/                      # GitHub workflows
    └── workflows/
        └── deploy-timeline.yml   # Automated deployment
```

## 🚀 Quick Start

### Generate Complete Experiment Overview
```bash
python scripts/generate_overview_csv.py
```
This creates `data/processed/auto_generated_overview.csv` with all experiment data.

### Add New Experiment
```bash
python scripts/add_experiment.py
```

### Generate Timeline Visualization
```bash
python scripts/generate_timeline.py
```

## 📊 Data Description

### Main Dataset: `auto_generated_overview.csv`
Contains comprehensive experiment information with the following columns:

| Column | Description |
|--------|-------------|
| Group | Experiment group (exp_cell, exp_cerebellum, etc.) |
| Setup | Unique setup identifier |
| Target | Target organelles (mito, nuc, cell, er+isg+ld+lyso+mito+nuc) |
| Model Type | Architecture type (fly model, isolated_unet) |
| Starting Checkpoint | Initial model checkpoint |
| Max Iterations | Maximum training iterations |
| Resolution (nm) | Voxel resolution in nanometers |
| Batch Size | Training batch size |
| Learning Rate | Training learning rate |
| Creation Date | Experiment creation date |
| Still Running | Whether experiment is currently active |
| LSD | Whether experiment uses Local Shape Descriptors |

## 🔧 Key Features

### Automated Data Extraction
- **Smart Directory Scanning**: Automatically discovers experiments across multiple project directories
- **Configuration Parsing**: Extracts parameters from `config.yaml` and `train.py` files
- **Checkpoint Analysis**: Determines training progress and starting points
- **LSD Detection**: Identifies Local Shape Descriptor usage from code analysis

### Target Detection
- **Config-based**: Extracts organelle targets from segmentation labels
- **Name-based**: Infers targets from experiment naming conventions
- **Multi-organelle Support**: Handles complex multi-target experiments

### Data Quality
- **Filtering**: Excludes incomplete experiments without checkpoints
- **Validation**: Compares automated vs manual data for accuracy
- **Deduplication**: Removes duplicate entries and consolidates data

## 📈 Current Statistics

- **75 total experiments** tracked
- **17 experiments** using LSD (Local Shape Descriptors)
- **58 experiments** using standard approaches
- **95% accuracy** compared to manual curation

### Target Distribution
- `er+isg+ld+lyso+mito+nuc`: 40 experiments (multi-organelle)
- `mito`: 13 experiments (mitochondria)
- `cell`: 7 experiments (cell segmentation)
- `nuc`: 4 experiments (nucleus)
- Other specific combinations: 11 experiments

## 🛠 Development

### Adding New Experiment Types
1. Update scanning logic in `scripts/generate_overview_csv.py`
2. Add new directory patterns to `scan_experiment_directories()`
3. Test with sample data

### Extending Target Detection
1. Modify `extract_additional_config_info()` function
2. Add new organelle patterns to detection logic
3. Update target inference rules

## 📝 Dependencies

Install required packages:
```bash
pip install -r config/requirements.txt
```

Key dependencies:
- `pyyaml`: Configuration file parsing
- `pandas`: Data manipulation
- `pathlib`: File system operations

## 🤝 Contributing

1. Follow the established directory structure
2. Update documentation when adding features
3. Test with existing experiment data
4. Maintain data quality and validation

## 📞 Contact

For questions about specific experiments or data interpretation, please refer to the individual experiment directories or contact the research team.



### 🥞 Pancreas Experiments (`exp_pancreas`)

| Setup | Target | Model Type | Starting Checkpoint | Max Iterations | Resolution (nm) | Batch Size | Learning Rate | Creation Date | Still Running |
|-------|--------|------------|-------------------|----------------|-----------------|------------|---------------|---------------|---------------|
| setup_07 | mito | fly model | 20250806_mito_mouse_distance_16nm/362k | 490,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |
| setup_08 | mito | fly model | 20250725_mito_all_mixed_distance_16nm/568k | 490,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |
| setup_09 | nuc | fly model | 20250806_nuc_mouse_distance_32nm/342k | 500,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |
| setup_10 | nuc | fly model | 20250806_nuc_mouse_distance_32nm/342k | 490,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |
| setup_12 | isg+ld+lyso+mito | fly model | 20250711_isg_ld_all_1/244k | 420,000 | 16 | 14 | 5.0e-06 | 2025-09-03 | NO |
| setup_13 | isg | fly model | 20250711_isg_ld_all_1/244k | 430,000 | 16 | 14 | 5.0e-06 | 2025-09-03 | NO |
| setup_14 | isg+ld+lyso | fly model | 20250711_isg_ld_all_1/244k | 420,000 | 16 | 14 | 5.0e-06 | 2025-09-03 | NO |

### 🧬 Cell Experiments (`exp_cell`)

| Setup | Target | Model Type | Starting Checkpoint | Max Iterations | Resolution (nm) | Batch Size | Learning Rate | Creation Date | Still Running |
|-------|--------|------------|-------------------|----------------|-----------------|------------|---------------|---------------|---------------|
| setup_20 | cell | isolated_unet | config_2/278361 | 100,000 | 8 | 14 | 5.0e-05 | 2025-09-29 | YES |
| setup_21 | cell | isolated_unet | config_2/278361 | 50,000 | 16 | 10 | 5.0e-05 | 2025-09-28 | YES |
| setup_22 | cell | isolated_unet | config_2/278361 | 50,000 | 32 | 10 | 5.0e-05 | 2025-09-28 | YES |
| setup_23 | cell | isolated_unet | config_2/278361 | 50,000 | 64 | 10 | 5.0e-05 | 2025-09-28 | YES |
| setup_24 | cell | isolated_unet | config_2/278361 | 50,000 | 128 | 10 | 5.0e-05 | 2025-09-28 | YES |
| setup_33 | cell | isolated_unet | run07/432k | N/A | 8 | 14 | 5.0e-06 | 2025-09-29 | YES |
| setup_34 | cell | isolated_unet | run07/432k | N/A | 64 | 14 | 5.0e-06 | 2025-09-29 | NO |

### 🧠 Cerebellum Experiments (`exp_cerebellum`)

| Setup | Target | Model Type | Starting Checkpoint | Max Iterations | Resolution (nm) | Batch Size | Learning Rate | Creation Date | Still Running |
|-------|--------|------------|-------------------|----------------|-----------------|------------|---------------|---------------|---------------|
| setup_0 | mito | fly model | 20250725_mito_all_mixed_distance_16nm/568k | 510,000 | 16 | 14 | 5.0e-06 | 2025-08-27 | NO |
| setup_1 | mito | fly model | 20250725_mito_all_mixed_distance_16nm/80k | 500,000 | 16 | 14 | 5.0e-06 | 2025-08-27 | NO |
| setup_2 | mito | fly model | 20250725_mito_all_mixed_distance_16nm/568k | 500,000 | 16 | 14 | 5.0e-06 | 2025-08-27 | NO |
| setup_3 | mito | fly model | 20250725_mito_all_mixed_distance_16nm/80k | 500,000 | 16 | 14 | 5.0e-06 | 2025-08-27 | NO |
| setup_4 | mito | fly model | 20250725_mito_all_mixed_distance_16nm/568k | 500,000 | 16 | 14 | 5.0e-06 | 2025-08-28 | NO |
| setup_5 | mito | fly model | 20250725_mito_all_mixed_distance_16nm/80k | 500,000 | 16 | 14 | 5.0e-06 | 2025-08-30 | NO |
| setup_6 | nuc | fly model | 20250725_nuc_all_mixed_distance_32nm/80k | 490,000 | 16 | 14 | 5.0e-06 | 2025-08-30 | NO |
| setup_11 | nuc | fly model | 20250725_nuc_all_mixed_distance_32nm/80k | 480,000 | 16 | 14 | 5.0e-06 | 2025-09-24 | NO |

### 🧠 C. elegans v2 Experiments (`exp_c-elegen/v2`)

| Setup | Target | Model Type | Starting Checkpoint | Max Iterations | Resolution (nm) | Creation Date | Still Running |
|-------|--------|------------|-------------------|----------------|-----------------|---------------|---------------|
| train_fly_model | various | fly model | from scratch | - | - | - | NO |

### 🧠 C. elegans v3 Experiments (`exp_c-elegen/v3`)

| Setup | Target | Model Type | Starting Checkpoint | Max Iterations | Resolution (nm) | Creation Date | Still Running |
|-------|--------|------------|-------------------|----------------|-----------------|---------------|---------------|
| 20250725_mito_all_mixed_distance_16nm | mito | fly model | from scratch | 80,000 | 16 | 2025-07-25 | NO |
| 20250725_mito_all_distance_16nm | mito | fly model | from scratch | 80,000+ | 16 | 2025-07-25 | NO |
| 20250725_nuc_all_mixed_distance_32nm | nucleus | fly model | from scratch | 80,000+ | 32 | 2025-07-25 | NO |
| 20250806_mito_mouse_distance_16nm | mito | fly model | from scratch | 568,000+ | 16 | 2025-08-06 | NO |
| 20250806_nuc_mouse_distance_32nm | nucleus | fly model | from scratch | 342,000+ | 32 | 2025-08-06 | NO |
| [+80 more organelle runs] | various | fly model | from scratch | varies | 16-64 | 2025-07-25/08-06 | NO |

### 🧠 C. elegans v4 Experiments (`exp_c-elegen/v4`)

| Setup | Target | Model Type | Starting Checkpoint | Max Iterations | Resolution (nm) | Creation Date | Still Running |
|-------|--------|------------|-------------------|----------------|-----------------|---------------|---------------|
| setup_25 | ld+lyso+mito+nuc+perox+yolk | fly model | run07/432k | 160,000 | 8 | 2025-09-29 | YES |
| setup_26 | ld+lyso+mito+nuc+perox+yolk | fly model | run07/432k | 170,000 | 16 | 2025-09-29 | YES |
| setup_27 | ld+lyso+mito+nuc+yolk | fly model | run07/432k | 150,000 | 8 | 2025-09-29 | YES |
| setup_28 | ld+lyso+mito+nuc+yolk | fly model | run07/432k | 160,000 | 16 | 2025-09-29 | YES |
| setup_29 | er | fly model | run07/432k | 180,000 | 8 | 2025-09-29 | YES |
| setup_31 | ecs | fly model | run07/432k | 180,000 | 8 | 2025-09-29 | YES |
| setup_32 | ecs | fly model | run07/432k | 190,000 | 16 | 2025-09-29 | YES |

## Experiment Groups

### 🥞 Pancreas (`exp_pancreas`)
- **Focus**: Mitochondria segmentation in pancreatic tissue
- **Model Base**: Fly model architecture
- **Resolution**: 16nm voxel size
- **Training Data**: JRC mouse pancreas datasets (samples 4-7)
- **Setups**: setup_07, setup_08, setup_09, setup_10, setup_12, setup_13, setup_14

### 🧬 Cell (`exp_cell`)
- **Focus**: Cell boundary segmentation
- **Model Base**: Isolated U-Net architecture
- **Resolution**: 8nm voxel size  
- **Training Data**: Multi-crop nucleus datasets with segmentation
- **Setups**: setup_20, setup_21, setup_22, setup_23, setup_24, setup_33, setup_34

### 🧠 C. elegans (`exp_c-elegen`)
- **Focus**: Various organelle segmentation in C. elegans
- **Status**: Base models for transfer learning
- **Versions**: 
  - **v2**: Early fly model experiments
  - **v3**: Comprehensive organelle models (85+ runs covering mito, nucleus, ER, lyso, etc.)
  - **v4**: Latest setups (setup_25-32)

### 🔬 Mitochondria (`exp_mito`)
- **Focus**: Mitochondria segmentation with LSD loss
- **Model Base**: Fly model architecture
- **Resolution**: 16nm voxel size
- **Training Data**: Mixed datasets for mitochondria detection
- **Setups**: setup_15, setup_16, setup_17, setup_18, setup_19

### 💧 Salivary Gland (`exp_salivary`)
- **Focus**: Mitochondria and nucleus in salivary gland tissue
- **Model Base**: Transfer from other experiments
- **Status**: Production inference runs

### 🧠 Cerebellum (`exp_cerebellum`)
- **Focus**: Mitochondria segmentation in cerebellar tissue
- **Model Base**: Fly model architecture
- **Resolution**: 16nm voxel size
- **Training Data**: JRC mouse cerebellum datasets
- **Setups**: setup_0, setup_1, setup_2, setup_3, setup_4, setup_5, setup_6, setup_11

## Model Architectures

### Fly Model
- **Type**: Standard DaCapo model architecture
- **Usage**: Pancreas experiments
- **Starting Point**: C. elegans trained models

### Isolated U-Net
- **Type**: Custom U-Net implementation
- **Usage**: Cell boundary experiments
- **Configurations**: Various context sizes (112, 162)

## File Structure

```
exp_[group]/
├── runs/
│   ├── setup_XX/
│   │   ├── config.yaml          # Training configuration
│   │   ├── model_checkpoint_*   # Saved model states
│   │   ├── error.log           # Training logs
│   │   └── validation/         # Validation outputs
│   └── submit.py               # Job submission scripts
├── flow/                       # Flow execution configs
└── yamls/                      # Dataset configurations
```

## Usage Notes

- **Checkpoints**: Model states are saved every 10k iterations
- **Validation**: Periodic validation runs track training progress
- **Transfer Learning**: Models often start from pre-trained checkpoints
- **Resolution**: Higher resolution (8nm) used for detailed cell boundaries, lower (16nm) for organelles

## Last Updated

September 29, 2025
