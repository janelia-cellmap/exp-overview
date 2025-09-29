
# Experiment Overview

This document is a comprehensive overview of all model training experiments and their configurations across different biological groups and setups.

## Training Experiments Summary

### 🔬 Mitochondria Experiments (`exp_mito`)
- **Focus**: Mitochondria segmentation with LSD loss
- **Model Base**: Fly model architecture
- **Resolution**: 16nm voxel size
- **Training Data**: Mixed datasets for mitochondria detection
- **Setups**: setup_15, setup_16, setup_17, setup_18, setup_19

| Setup | Target | Model Type | Starting Checkpoint | Max Iterations | Resolution (nm) | Batch Size | Learning Rate | Still Running |
|-------|--------|------------|-------------------|----------------|-----------------|------------|---------------|---------------|
| setup_15 | mito | fly model | 20250806_mito_mouse_distance_16nm/362k | 90,000 | 16 | 14 | 5.0e-05 | YES |
| setup_16 | mito | fly model | setup_15/80k | 90,000 | 16 | 14 | 5.0e-05 | YES |
| setup_17 | mito | fly model | setup_16/30k | 90,000 | 16 | 14 | 5.0e-05 | YES |
| setup_18 | mito | fly model | 20250725_mito_all_mixed_distance_16nm/372k | 90,000 | 16 | 14 | 5.0e-05 | YES |
| setup_19 | mito | fly model | 20250725_mito_all_mixed_distance_16nm/372k | 90,000 | 16 | 14 | 5.0e-05 | YES |



### 🥞 Pancreas Experiments (`exp_pancreas`)

| Setup | Target | Model Type | Starting Checkpoint | Max Iterations | Resolution (nm) | Batch Size | Learning Rate | Creation Date | Still Running |
|-------|--------|------------|-------------------|----------------|-----------------|------------|---------------|---------------|---------------|
| setup_07 | mito | fly model | 20250806_mito_mouse_distance_16nm/362k | 90,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |
| setup_08 | mito | fly model | 20250725_mito_all_mixed_distance_16nm/568k | 90,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |
| setup_09 | mito | fly model | 20250806_nuc_mouse_distance_32nm/342k | 90,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |
| setup_10 | mito | fly model | 20250806_nuc_mouse_distance_32nm/342k | 90,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |
| setup_12 | mito | fly model | 20250711_isg_ld_all_1/244k | 90,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |
| setup_13 | mito | fly model | 20250711_isg_ld_all_1/244k | 90,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |
| setup_14 | mito | fly model | 20250711_isg_ld_all_1/244k | 90,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |

### 🧬 Cell Experiments (`exp_cell`)

| Setup | Target | Model Type | Starting Checkpoint | Max Iterations | Resolution (nm) | Batch Size | Learning Rate | Creation Date | Still Running |
|-------|--------|------------|-------------------|----------------|-----------------|------------|---------------|---------------|---------------|
| setup_20 | cell | isolated_unet | config_2/278361 | 90,000 | 8 | 14 | 5.0e-05 | 2025-09-29 | YES |
| setup_21 | cell | isolated_unet | config_2/278361 | 50,000 | 16 | 10 | 5.0e-05 | 2025-09-28 | YES |
| setup_22 | cell | isolated_unet | config_2/278361 | 50,000 | 32 | 10 | 5.0e-05 | 2025-09-28 | YES |
| setup_23 | cell | isolated_unet | config_2/278361 | 50,000 | 64 | 10 | 5.0e-05 | 2025-09-28 | YES |
| setup_24 | cell | isolated_unet | config_2/278361 | 50,000 | 128 | 10 | 5.0e-05 | 2025-09-28 | YES |
| setup_33 | cell | isolated_unet | run07/432k | N/A | 8 | 14 | 5.0e-06 | 2025-09-29 | YES |
| setup_34 | cell | isolated_unet | run07/432k | N/A | 64 | 14 | 5.0e-06 | 2025-09-29 | NO |

### 🧠 Cerebellum Experiments (`exp_cerebellum`)

| Setup | Target | Model Type | Starting Checkpoint | Max Iterations | Resolution (nm) | Batch Size | Learning Rate | Creation Date | Still Running |
|-------|--------|------------|-------------------|----------------|-----------------|------------|---------------|---------------|---------------|
| setup_0 | mito | fly model | 20250725_mito_all_mixed_distance_16nm/568k | 90,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |
| setup_1 | mito | fly model | 20250725_mito_all_mixed_distance_16nm/80k | 90,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |
| setup_2 | mito | fly model | 20250725_mito_all_mixed_distance_16nm/568k | 90,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |
| setup_3 | mito | fly model | 20250725_mito_all_mixed_distance_16nm/80k | 90,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |
| setup_4 | mito | fly model | 20250725_mito_all_mixed_distance_16nm/568k | 90,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |
| setup_5 | mito | fly model | 20250725_mito_all_mixed_distance_16nm/80k | 90,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |
| setup_6 | mito | fly model | 20250725_nuc_all_mixed_distance_32nm/80k | 90,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |
| setup_11 | mito | fly model | 20250725_nuc_all_mixed_distance_32nm/80k | 90,000 | 16 | 14 | 5.0e-06 | 2025-09-23 | NO |

### 🧠 C. elegans v2 Experiments (`exp_c-elegen/v2`)

| Setup | Target | Model Type | Starting Checkpoint | Max Iterations | Resolution (nm) | Creation Date | Still Running |
|-------|--------|------------|-------------------|----------------|-----------------|---------------|---------------|
| train_fly_model | various | fly model | from scratch | TBD | TBD | - | NO |

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
| setup_25 | mito+nuc+lyso | fly model | run07/432k | 90,000 | 8 | 2025-09-29 | YES |
| setup_26 | mito+nuc+lyso | fly model | run07/432k | 90,000 | 16 | 2025-09-29 | YES |
| setup_27 | mito+nuc+lyso | fly model | run07/432k | 90,000 | 8 | 2025-09-29 | YES |
| setup_28 | mito+nuc+lyso | fly model | run07/432k | 90,000 | 16 | 2025-09-29 | YES |
| setup_29 | er | fly model | run07/432k | 90,000 | 8 | 2025-09-29 | YES |
| setup_31 | ecs | fly model | run07/432k | 90,000 | 8 | 2025-09-29 | YES |
| setup_32 | ecs | fly model | run07/432k | 90,000 | 16 | 2025-09-29 | YES |

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
